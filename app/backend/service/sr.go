/*
 * Copyright 2025 Bronya0 <tangssst@163.com>.
 * Author Github: https://github.com/Bronya0
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package service

import (
	"app/backend/types"
	"context"
	"crypto/tls"
	"encoding/base64"
	"encoding/binary"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"strings"
	"time"

	"github.com/hamba/avro/v2"
	"github.com/twmb/franz-go/pkg/sr"
)

// SetSchemaRegistry 配置 Schema Registry 连接（URL、Basic 认证、跳过 TLS 验证）。
// 连接成功后，Consumer 页面即可选择 avro / sr_json / sr_pb 解码。
func (k *Service) SetSchemaRegistry(url string, user string, pass string, skipTLS bool) *types.ResultResp {
	result := &types.ResultResp{}
	if url == "" {
		k.clearSR()
		result.Err = "url is required"
		return result
	}
	if !strings.HasPrefix(url, "http://") && !strings.HasPrefix(url, "https://") {
		url = "http://" + url
	}

	opts := []sr.ClientOpt{sr.URLs(url)}
	if user != "" {
		opts = append(opts, sr.BasicAuth(user, pass))
	}
	if skipTLS {
		opts = append(opts, sr.DialTLSConfig(&tls.Config{InsecureSkipVerify: true}))
	}

	cl, err := sr.NewClient(opts...)
	if err != nil {
		result.Err = "SchemaRegistry NewClient Error：" + err.Error()
		return result
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	if _, err := cl.Subjects(ctx); err != nil {
		result.Err = "SchemaRegistry connect failed：" + err.Error()
		return result
	}

	k.srMu.Lock()
	k.srClient = cl
	k.srCodecs = map[int]string{}
	k.srURL = url
	k.srMu.Unlock()
	return result
}

// GetSRStatus 返回 Schema Registry 的当前连接状态。
func (k *Service) GetSRStatus() *types.ResultResp {
	result := &types.ResultResp{}
	k.srMu.Lock()
	defer k.srMu.Unlock()
	connected := k.srClient != nil
	result.Result = map[string]any{
		"connected": connected,
		"url":       k.srURL,
	}
	return result
}

// GetSRSubjects 列出所有 subject 及版本数、兼容性级别。
func (k *Service) GetSRSubjects() *types.ResultsResp {
	result := &types.ResultsResp{Results: make([]any, 0)}
	cl, err := k.getSRClient()
	if err != nil {
		result.Err = err.Error()
		return result
	}
	ctx, cancel := context.WithTimeout(context.Background(), 20*time.Second)
	defer cancel()

	subjects, err := cl.Subjects(ctx)
	if err != nil {
		result.Err = "Subjects Error：" + err.Error()
		return result
	}

	compatResults := cl.Compatibility(ctx, subjects...)
	compatMap := map[string]string{}
	for _, c := range compatResults {
		if c.Subject != "" {
			compatMap[c.Subject] = c.Level.String()
		}
	}

	for _, s := range subjects {
		versions, _ := cl.SubjectVersions(ctx, s)
		result.Results = append(result.Results, map[string]any{
			"subject":       s,
			"version_count": len(versions),
			"compatibility": compatMap[s],
		})
	}
	return result
}

// GetSRSubjectVersions 列出 subject 的所有版本号。
func (k *Service) GetSRSubjectVersions(subject string) *types.ResultResp {
	result := &types.ResultResp{}
	cl, err := k.getSRClient()
	if err != nil {
		result.Err = err.Error()
		return result
	}
	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()
	versions, err := cl.SubjectVersions(ctx, subject)
	if err != nil {
		result.Err = "SubjectVersions Error：" + err.Error()
		return result
	}
	result.Result = map[string]any{"versions": versions}
	return result
}

// GetSRSchema 获取 subject 某个版本的 schema 全文与元信息。version 传 -1 表示最新版本。
func (k *Service) GetSRSchema(subject string, version int) *types.ResultResp {
	result := &types.ResultResp{}
	cl, err := k.getSRClient()
	if err != nil {
		result.Err = err.Error()
		return result
	}
	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()
	if version < 0 {
		vs, err := cl.SubjectVersions(ctx, subject)
		if err != nil {
			result.Err = "SubjectVersions Error：" + err.Error()
			return result
		}
		if len(vs) == 0 {
			result.Err = "no versions for subject " + subject
			return result
		}
		version = vs[len(vs)-1]
	}
	ss, err := cl.SchemaByVersion(ctx, subject, version)
	if err != nil {
		result.Err = "SchemaByVersion Error：" + err.Error()
		return result
	}
	refs := make([]any, 0)
	for _, r := range ss.References {
		refs = append(refs, map[string]any{
			"name":    r.Name,
			"subject": r.Subject,
			"version": r.Version,
		})
	}
	result.Result = map[string]any{
		"subject": ss.Subject,
		"version": ss.Version,
		"id":      ss.ID,
		"type":    ss.Type.String(),
		"schema":  ss.Schema,
		"refs":    refs,
	}
	return result
}

// DeleteSRSubject 删除 subject（软删除；hard 为 true 时先软删后硬删）。
func (k *Service) DeleteSRSubject(subject string, hard bool) *types.ResultResp {
	result := &types.ResultResp{}
	cl, err := k.getSRClient()
	if err != nil {
		result.Err = err.Error()
		return result
	}
	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()
	versions, err := cl.DeleteSubject(ctx, subject, sr.SoftDelete)
	if err != nil {
		result.Err = "DeleteSubject Error：" + err.Error()
		return result
	}
	if hard {
		if _, err := cl.DeleteSubject(ctx, subject, sr.HardDelete); err != nil {
			result.Err = "DeleteSubject(hard) Error：" + err.Error()
			return result
		}
	}
	result.Result = map[string]any{"deleted_versions": versions}
	return result
}

// DeleteSRSchemaVersion 删除 subject 的某个版本（软删除）。
func (k *Service) DeleteSRSchemaVersion(subject string, version int) *types.ResultResp {
	result := &types.ResultResp{}
	cl, err := k.getSRClient()
	if err != nil {
		result.Err = err.Error()
		return result
	}
	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()
	if err := cl.DeleteSchema(ctx, subject, version, sr.SoftDelete); err != nil {
		result.Err = "DeleteSchema Error：" + err.Error()
		return result
	}
	return result
}

// SetSRCompatibility 设置 subject（或全局，subject 为空）的兼容性级别。
// level: NONE / BACKWARD / BACKWARD_TRANSITIVE / FORWARD / FORWARD_TRANSITIVE / FULL / FULL_TRANSITIVE
func (k *Service) SetSRCompatibility(subject string, level string) *types.ResultResp {
	result := &types.ResultResp{}
	cl, err := k.getSRClient()
	if err != nil {
		result.Err = err.Error()
		return result
	}
	l, ok := srCompatLevel(level)
	if !ok {
		result.Err = "unsupported compatibility level: " + level
		return result
	}
	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()
	sc := sr.SetCompatibility{Level: l}
	var res []sr.CompatibilityResult
	if subject == "" {
		res = cl.SetCompatibility(ctx, sc)
	} else {
		res = cl.SetCompatibility(ctx, sc, subject)
	}
	for _, r := range res {
		if r.Err != nil {
			result.Err = "SetCompatibility Error：" + r.Err.Error()
			return result
		}
	}
	result.Result = map[string]any{"level": l.String()}
	return result
}

func srCompatLevel(level string) (sr.CompatibilityLevel, bool) {
	switch strings.ToUpper(level) {
	case "NONE":
		return sr.CompatNone, true
	case "BACKWARD":
		return sr.CompatBackward, true
	case "BACKWARD_TRANSITIVE":
		return sr.CompatBackwardTransitive, true
	case "FORWARD":
		return sr.CompatForward, true
	case "FORWARD_TRANSITIVE":
		return sr.CompatForwardTransitive, true
	case "FULL":
		return sr.CompatFull, true
	case "FULL_TRANSITIVE":
		return sr.CompatFullTransitive, true
	}
	return 0, false
}

// ClearSchemaRegistry 清除 Schema Registry 连接（应用退出或断开集群时调用）。
func (k *Service) ClearSchemaRegistry() {
	k.clearSR()
}

func (k *Service) getSRClient() (*sr.Client, error) {
	k.srMu.Lock()
	defer k.srMu.Unlock()
	if k.srClient == nil {
		return nil, fmt.Errorf("schema registry is not connected, please configure it on the Schema Registry page")
	}
	return k.srClient, nil
}

func (k *Service) clearSR() {
	k.srMu.Lock()
	k.srClient = nil
	k.srURL = ""
	k.srCodecs = map[int]string{}
	k.srMu.Unlock()
}

// ---- Confluent wire format 解码 ----

// decodeValue 按 decode 选项把消息字节转成字符串。
// decode:
//   - "" / "utf8": 原样字符串
//   - "base64":    消息内容本身是 base64 编码，解码为原始字节
//   - "avro":      Confluent Avro wire format（需要 Schema Registry）
//   - "sr_json":   Confluent JSON Schema（去 5 字节头后即为 JSON 文本）
//   - "sr_pb":     Confluent Protobuf（显示 schemaId 与 payload hex）
func (k *Service) decodeValue(data []byte, decode string) (string, error) {
	switch strings.ToLower(decode) {
	case "base64":
		decoded, err := base64.StdEncoding.DecodeString(string(data))
		if err != nil {
			return string(data), nil // 解不出来就原样返回
		}
		return string(decoded), nil
	case "avro":
		return k.decodeConfluentAvro(data)
	case "sr_json":
		payload, id, err := stripConfluentHeader(data)
		if err != nil {
			return string(data), nil // 无头，原样返回
		}
		_ = id
		return string(payload), nil
	case "sr_pb":
		payload, id, err := stripConfluentHeader(data)
		if err != nil {
			return string(data), nil
		}
		return fmt.Sprintf("schemaId=%d\npayload(hex)=%s", id, hex.EncodeToString(payload)), nil
	default:
		return string(data), nil
	}
}

// stripConfluentHeader 剥离 Confluent wire format 头（magic 0x00 + 4 字节 schemaId）。
func stripConfluentHeader(data []byte) (payload []byte, schemaID int, err error) {
	if len(data) < 5 || data[0] != 0 {
		return nil, 0, fmt.Errorf("not a confluent wire format message")
	}
	return data[5:], int(binary.BigEndian.Uint32(data[1:5])), nil
}

// decodeConfluentAvro 解码 Confluent Avro 消息：从 Schema Registry 取 schema 编译后解码为 JSON。
func (k *Service) decodeConfluentAvro(data []byte) (string, error) {
	payload, schemaID, err := stripConfluentHeader(data)
	if err != nil {
		return "", err
	}
	schema, err := k.avroSchemaByID(schemaID)
	if err != nil {
		return "", err
	}
	parsed, err := avro.Parse(schema)
	if err != nil {
		return "", fmt.Errorf("parse avro schema failed: %w", err)
	}
	var v any
	if err := avro.Unmarshal(parsed, payload, &v); err != nil {
		return "", fmt.Errorf("avro unmarshal failed: %w", err)
	}
	out, err := json.Marshal(v)
	if err != nil {
		return "", err
	}
	return string(out), nil
}

// avroSchemaByID 按 schemaId 获取 schema 全文（带进程内缓存）。
func (k *Service) avroSchemaByID(id int) (string, error) {
	k.srMu.Lock()
	cl := k.srClient
	if cl == nil {
		k.srMu.Unlock()
		return "", fmt.Errorf("schema registry is not connected")
	}
	if s, ok := k.srCodecs[id]; ok {
		k.srMu.Unlock()
		return s, nil
	}
	k.srMu.Unlock()

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	ss, err := cl.SchemaByID(ctx, id)
	if err != nil {
		return "", fmt.Errorf("SchemaByID(%d) failed: %w", id, err)
	}
	s := ss.Schema

	k.srMu.Lock()
	if k.srCodecs == nil {
		k.srCodecs = map[int]string{}
	}
	k.srCodecs[id] = s
	k.srMu.Unlock()
	return s, nil
}
