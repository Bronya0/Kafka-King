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
	"context"
	"encoding/binary"
	"fmt"
	"strings"
	"sync"
	"testing"
	"time"

	"github.com/hamba/avro/v2"
	"github.com/twmb/franz-go/pkg/kfake"
	"github.com/twmb/franz-go/pkg/kgo"
	"github.com/twmb/franz-go/pkg/sr"
	"github.com/twmb/franz-go/pkg/sr/srfake"
)

const testAvroSchema = `{"type":"record","name":"kv","fields":[{"name":"id","type":"int"},{"name":"name","type":"string"}]}`

// avroEncode 用 Confluent wire format（0x00 + be32 schemaID + avro 数据）编码
func avroEncode(schemaID int, v map[string]any) ([]byte, error) {
	parsed, err := avro.Parse(testAvroSchema)
	if err != nil {
		return nil, err
	}
	data, err := avro.Marshal(parsed, v)
	if err != nil {
		return nil, err
	}
	out := make([]byte, 5, 5+len(data))
	out[0] = 0
	binary.BigEndian.PutUint32(out[1:5], uint32(schemaID))
	return append(out, data...), nil
}

// newFakeCluster 启动一个 kfake 假集群并建立 Service 连接。
func newFakeCluster(t *testing.T, seedTopics ...string) (*Service, *kfake.Cluster) {
	t.Helper()
	opts := []kfake.Opt{kfake.NumBrokers(1)}
	if len(seedTopics) > 0 {
		opts = append(opts, kfake.SeedTopics(3, seedTopics...))
	}
	c, err := kfake.NewCluster(opts...)
	if err != nil {
		t.Fatalf("kfake.NewCluster: %v", err)
	}
	t.Cleanup(c.Close)

	s := NewKafkaService()
	addrs := strings.Join(c.ListenAddrs(), ",")
	res := s.SetConnect("test", map[string]any{
		"name":              "test",
		"bootstrap_servers": addrs,
		"tls":               "disable",
		"sasl":              "disable",
		"use_ssh":           "disable",
	}, false)
	if res.Err != "" {
		t.Fatalf("SetConnect: %s", res.Err)
	}
	return s, c
}

func mustOk(t *testing.T, op string, err string) {
	t.Helper()
	if err != "" {
		t.Fatalf("%s failed: %s", op, err)
	}
}

// offsetAt 取某 topic 某分区的 At 值
func offsetAt(t *testing.T, m map[string]map[int32]any, topic string, part int32) int64 {
	t.Helper()
	row, ok := m[topic][part].(map[string]any)
	if !ok {
		t.Fatalf("offset[%s][%d] missing", topic, part)
	}
	return row["At"].(int64)
}

// offsetMap 从 GetTopicOffsets 的 Result 中取出 map[string]map[int32]any
func offsetMap(t *testing.T, m map[string]any, key string) map[string]map[int32]any {
	t.Helper()
	v, ok := m[key].(map[string]map[int32]any)
	if !ok {
		t.Fatalf("result[%q] is not an offset map: %T", key, m[key])
	}
	return v
}

func TestFakeConnectAndTopics(t *testing.T) {
	s, _ := newFakeCluster(t, "seeded")

	res := s.GetTopics(true)
	mustOk(t, "GetTopics", res.Err)
	found := false
	for _, r := range res.Results {
		if m, ok := r.(map[string]any); ok && m["topic"] == "seeded" {
			found = true
			if m["partition_count"].(int) != 3 {
				t.Fatalf("expected 3 partitions, got %v", m["partition_count"])
			}
		}
	}
	if !found {
		t.Fatal("seeded topic not found")
	}

	mustOk(t, "CreateTopics", s.CreateTopics([]string{"t1", "t2"}, 2, 1, nil).Err)
	mustOk(t, "GetTopicConfig", s.GetTopicConfig("t1").Err)
	mustOk(t, "CreatePartitions", s.CreatePartitions([]string{"t1"}, 3).Err)
	mustOk(t, "DeleteTopic", s.DeleteTopic([]string{"t2"}).Err)

	res = s.GetTopics(true)
	for _, r := range res.Results {
		if m, ok := r.(map[string]any); ok && m["topic"] == "t1" {
			if m["partition_count"].(int) != 3 {
				t.Fatalf("t1 partitions after add: %v", m["partition_count"])
			}
		}
	}
}

func TestFakeBrokers(t *testing.T) {
	s, _ := newFakeCluster(t)
	res := s.GetBrokers()
	mustOk(t, "GetBrokers", res.Err)
	brokers, _ := res.Result["brokers"].([]map[string]any)
	if len(brokers) != 1 {
		t.Fatalf("expected 1 broker, got %d", len(brokers))
	}
	if controllers, ok := res.Result["controller_id"].(int32); !ok || controllers < 0 {
		t.Logf("controller_id = %v", res.Result["controller_id"])
	}
}

func TestFakeProduceConsume(t *testing.T) {
	s, _ := newFakeCluster(t, "topic-c")

	for i := 0; i < 10; i++ {
		res := s.Produce("topic-c", fmt.Sprintf("k%d", i), fmt.Sprintf("v%d", i), -1, 1, nil, "")
		mustOk(t, fmt.Sprintf("Produce #%d", i), res.Err)
	}
	// 指定分区发送
	mustOk(t, "Produce partition=0", s.Produce("topic-c", "p", "pv", 0, 2, nil, "").Err)

	res := s.Consumer("topic-c", "__kafka_king_auto_generate__", 100, 10, "", "read_uncommitted", false, false, 0, 0, "utf8")
	mustOk(t, "Consumer", res.Err)
	if len(res.Results) != 12 {
		t.Fatalf("expected 12 messages, got %d", len(res.Results))
	}

	// 指定 offset 跳转（对每个分区生效）
	res = s.Consumer("topic-c", "__kafka_king_auto_generate__", 100, 10, "", "read_uncommitted", false, false, 0, 1, "utf8")
	mustOk(t, "Consumer startOffset=1", res.Err)
	if len(res.Results) == 0 || len(res.Results) >= 12 {
		t.Fatalf("expected fewer messages after offset jump, got %d", len(res.Results))
	}

}

func TestFakeGzipRoundTrip(t *testing.T) {
	s, _ := newFakeCluster(t, "topic-gz")

	mustOk(t, "Produce gzip", s.Produce("topic-gz", "g", "gz-value", -1, 1, nil, "gzip").Err)
	res := s.Consumer("topic-gz", "__kafka_king_auto_generate__", 100, 10, "gzip", "read_uncommitted", false, false, 0, 0, "utf8")
	mustOk(t, "Consumer gzip", res.Err)
	found := false
	for _, r := range res.Results {
		if m := r.(map[string]any); m["Value"] == "gz-value" {
			found = true
		}
	}
	if !found {
		t.Fatal("gzip round-trip value not found")
	}
}

func TestFakeReproduceMessages(t *testing.T) {
	s, _ := newFakeCluster(t, "topic-src", "topic-dst")

	mustOk(t, "Produce", s.Produce("topic-src", "k", "hello", -1, 3, nil, "").Err)
	res := s.Consumer("topic-src", "__kafka_king_auto_generate__", 10, 10, "", "read_uncommitted", false, false, 0, 0, "utf8")
	mustOk(t, "Consumer src", res.Err)
	if len(res.Results) != 3 {
		t.Fatalf("expected 3 messages, got %d", len(res.Results))
	}
	mustOk(t, "ReproduceMessages", s.ReproduceMessages("topic-dst", res.Results).Err)

	res = s.Consumer("topic-dst", "__kafka_king_auto_generate__", 10, 10, "", "read_uncommitted", false, false, 0, 0, "utf8")
	mustOk(t, "Consumer dst", res.Err)
	if len(res.Results) != 3 {
		t.Fatalf("expected 3 reproduced messages, got %d", len(res.Results))
	}
}

func TestFakeResetGroupOffsets(t *testing.T) {
	s, _ := newFakeCluster(t, "topic-r")

	mustOk(t, "Produce", s.Produce("topic-r", "k", "v", 0, 10, nil, "").Err)
	// 用固定 group 消费并提交
	res := s.Consumer("topic-r", "g-reset", 5, 10, "", "read_uncommitted", true, false, 0, 0, "utf8")
	mustOk(t, "Consumer", res.Err)
	if len(res.Results) != 5 {
		t.Fatalf("expected 5 messages, got %d", len(res.Results))
	}

	// 重置到 end
	reset := s.ResetGroupOffsets("g-reset", []string{"topic-r"}, "end", 0)
	mustOk(t, "ResetGroupOffsets(end)", reset.Err)

	// 验证提交位置 == end offset
	offs := s.GetTopicOffsets([]string{"topic-r"}, "g-reset")
	mustOk(t, "GetTopicOffsets", offs.Err)
	commitMap := offsetMap(t, offs.Result, "commit_map")
	endMap := offsetMap(t, offs.Result, "end_map")
	p0Commit := offsetAt(t, commitMap, "topic-r", 0)
	p0End := offsetAt(t, endMap, "topic-r", 0)
	if p0Commit != p0End {
		t.Fatalf("after reset end: commit=%d end=%d", p0Commit, p0End)
	}

	// 重置到 absolute
	reset = s.ResetGroupOffsets("g-reset", []string{"topic-r"}, "absolute", 2)
	mustOk(t, "ResetGroupOffsets(absolute)", reset.Err)
	offs = s.GetTopicOffsets([]string{"topic-r"}, "g-reset")
	commitMap = offsetMap(t, offs.Result, "commit_map")
	if at := offsetAt(t, commitMap, "topic-r", 0); at != 2 {
		t.Fatalf("after reset absolute: commit=%d", at)
	}
}

func TestFakeDeleteRecords(t *testing.T) {
	s, _ := newFakeCluster(t, "topic-d")

	mustOk(t, "Produce", s.Produce("topic-d", "k", "v", 0, 10, nil, "").Err)

	res := s.DeleteRecords("topic-d", nil, 5)
	mustOk(t, "DeleteRecords(5)", res.Err)

	offs := s.GetTopicOffsets([]string{"topic-d"}, "any-group")
	mustOk(t, "GetTopicOffsets", offs.Err)
	startMap := offsetMap(t, offs.Result, "start_map")
	if at := offsetAt(t, startMap, "topic-d", 0); at != 5 {
		t.Fatalf("after delete, start offset = %d, want 5", at)
	}

	// 删除全部
	res = s.DeleteRecords("topic-d", nil, -1)
	mustOk(t, "DeleteRecords(all)", res.Err)
	offs = s.GetTopicOffsets([]string{"topic-d"}, "any-group")
	startMap = offsetMap(t, offs.Result, "start_map")
	endMap := offsetMap(t, offs.Result, "end_map")
	if at := offsetAt(t, startMap, "topic-d", 0); at != offsetAt(t, endMap, "topic-d", 0) {
		t.Fatalf("after delete all: start=%d end=%d", at, offsetAt(t, endMap, "topic-d", 0))
	}
}

func TestFakeLogDirsQuotasReassignments(t *testing.T) {
	s, _ := newFakeCluster(t, "topic-l")

	res := s.GetLogDirs()
	mustOk(t, "GetLogDirs", res.Err)

	res = s.AlterPartitionReassignments("topic-l", map[string][]int32{"0": {0}})
	mustOk(t, "AlterPartitionReassignments", res.Err)

	res = s.ListReassignments([]string{"topic-l"})
	mustOk(t, "ListReassignments", res.Err)

	q := s.GetQuotas()
	mustOk(t, "GetQuotas", q.Err)

	mustOk(t, "AlterQuota(set)",
		s.AlterQuota("user", "alice", []map[string]any{
			{"key": "producer_byte_rate", "value": float64(102400)},
		}).Err)
	q = s.GetQuotas()
	mustOk(t, "GetQuotas(after set)", q.Err)
	found := false
	for _, r := range q.Results {
		if m := r.(map[string]any); strings.Contains(m["entity"].(string), "alice") {
			found = true
		}
	}
	if !found {
		t.Fatal("quota entity alice not found")
	}
	mustOk(t, "AlterQuota(remove)",
		s.AlterQuota("user", "alice", []map[string]any{
			{"key": "producer_byte_rate", "remove": true},
		}).Err)
}

func TestFakeACLs(t *testing.T) {
	s, _ := newFakeCluster(t)
	acl := map[string]any{
		"principal":      "User:alice",
		"resourceType":   "TOPIC",
		"resourceName":   "topic-l",
		"operation":      "READ",
		"permissionType": "ALLOW",
		"host":           "*",
	}
	mustOk(t, "CreateAcl", s.CreateAcl(acl).Err)
	got := s.GetAcls()
	mustOk(t, "GetAcls", got.Err)
	if len(got.Results) == 0 {
		t.Fatal("expected at least one acl")
	}
	mustOk(t, "DeleteAcl", s.DeleteAcl(acl).Err)
}

func TestFakeStreamMulti(t *testing.T) {
	s, _ := newFakeCluster(t, "stream-a", "stream-b")

	var mu sync.Mutex
	received := map[string]int{}
	ended := map[string]bool{}
	origHook := testEventHook
	testEventHook = func(name string, data any) {
		switch name {
		case "consumer-msg":
			if ev, ok := data.(streamMsgEvent); ok {
				mu.Lock()
				received[ev.ID] += len(ev.Rows)
				mu.Unlock()
			}
		case "consumer-end":
			if ev, ok := data.(streamEndEvent); ok {
				mu.Lock()
				ended[ev.ID] = true
				mu.Unlock()
			}
		}
	}
	defer func() { testEventHook = origHook }()

	mustOk(t, "StartStream a", s.StartStreamConsumer("s-a", "stream-a", "__kafka_king_auto_generate__", 10, 2, "", "read_uncommitted", false, false, 0, 0, "utf8").Err)
	mustOk(t, "StartStream b", s.StartStreamConsumer("s-b", "stream-b", "__kafka_king_auto_generate__", 10, 2, "", "read_uncommitted", false, false, 0, 0, "utf8").Err)

	// 两路流同时收到各自 topic 的消息
	mustOk(t, "Produce a", s.Produce("stream-a", "k", "a1", -1, 3, nil, "").Err)
	mustOk(t, "Produce b", s.Produce("stream-b", "k", "b1", -1, 2, nil, "").Err)

	deadline := time.Now().Add(15 * time.Second)
	for time.Now().Before(deadline) {
		mu.Lock()
		a, b := received["s-a"], received["s-b"]
		mu.Unlock()
		if a >= 3 && b >= 2 {
			break
		}
		time.Sleep(100 * time.Millisecond)
	}
	mu.Lock()
	a, b := received["s-a"], received["s-b"]
	mu.Unlock()
	if a < 3 || b < 2 {
		t.Fatalf("multi stream: s-a=%d s-b=%d", a, b)
	}

	// 停掉 a 后 b 仍能收到消息
	mustOk(t, "Stop a", s.StopStreamConsumer("s-a").Err)
	mustOk(t, "Produce b2", s.Produce("stream-b", "k", "b2", -1, 1, nil, "").Err)
	deadline = time.Now().Add(10 * time.Second)
	for time.Now().Before(deadline) {
		mu.Lock()
		b = received["s-b"]
		stopped := ended["s-a"]
		mu.Unlock()
		if b >= 3 && stopped {
			break
		}
		time.Sleep(100 * time.Millisecond)
	}
	mu.Lock()
	b = received["s-b"]
	mu.Unlock()
	if b < 3 {
		t.Fatalf("stream b should keep running after stopping a, got %d", b)
	}

	mustOk(t, "Stop all", s.StopStreamConsumer("").Err)
}

func TestFakeStreamCommit(t *testing.T) {
	s, _ := newFakeCluster(t, "stream-commit")

	mustOk(t, "Produce", s.Produce("stream-commit", "k", "v", 0, 5, nil, "").Err)
	mustOk(t, "StartStream",
		s.StartStreamConsumer("s-c", "stream-commit", "g-stream", 10, 2, "", "read_uncommitted", true, false, 0, 0, "utf8").Err)

	deadline := time.Now().Add(15 * time.Second)
	for time.Now().Before(deadline) {
		offs := s.GetTopicOffsets([]string{"stream-commit"}, "g-stream")
		if offs.Err == "" {
			if cm, ok := offs.Result["commit_map"].(map[string]map[int32]any); ok {
				if row, ok := cm["stream-commit"][0].(map[string]any); ok {
					if at, ok := row["At"].(int64); ok && at >= 5 {
						break
					}
				}
			}
		}
		time.Sleep(200 * time.Millisecond)
	}
	s.StopStreamConsumer("")

	offs := s.GetTopicOffsets([]string{"stream-commit"}, "g-stream")
	mustOk(t, "GetTopicOffsets", offs.Err)
	if at := offsetAt(t, offsetMap(t, offs.Result, "commit_map"), "stream-commit", 0); at < 5 {
		t.Fatalf("stream commit offset = %d, want >= 5", at)
	}
}

func TestFakeSchemaRegistryAndAvro(t *testing.T) {
	s, _ := newFakeCluster(t, "topic-avro")

	reg := srfake.New()
	defer reg.Close()
	if reg.URL() == "" {
		t.Fatal("srfake URL is empty")
	}

	schema := sr.Schema{
		Schema: testAvroSchema,
		Type:   sr.TypeAvro,
	}
	id, version, err := reg.RegisterSchema("topic-avro-value", schema)
	if err != nil {
		t.Fatalf("RegisterSchema: %v", err)
	}

	mustOk(t, "SetSchemaRegistry", s.SetSchemaRegistry(reg.URL(), "", "", false).Err)

	st := s.GetSRStatus()
	mustOk(t, "GetSRStatus", st.Err)
	if st.Result["connected"] != true {
		t.Fatal("SR should be connected")
	}

	subs := s.GetSRSubjects()
	mustOk(t, "GetSRSubjects", subs.Err)
	if len(subs.Results) != 1 {
		t.Fatalf("expected 1 subject, got %d", len(subs.Results))
	}

	sch := s.GetSRSchema("topic-avro-value", version)
	mustOk(t, "GetSRSchema", sch.Err)

	mustOk(t, "SetSRCompatibility", s.SetSRCompatibility("topic-avro-value", "BACKWARD").Err)

	// 构造 Confluent Avro wire 消息并生产
	codecPayload, err := avroEncode(id, map[string]any{"id": 1, "name": "hello"})
	if err != nil {
		t.Fatalf("avroEncode: %v", err)
	}
	record := &kgo.Record{Topic: "topic-avro", Value: codecPayload}
	cl := s.client
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	if err := cl.ProduceSync(ctx, record).FirstErr(); err != nil {
		t.Fatalf("produce avro: %v", err)
	}

	// 用 avro 解码消费
	res := s.Consumer("topic-avro", "__kafka_king_auto_generate__", 10, 10, "", "read_uncommitted", false, false, 0, 0, "avro")
	mustOk(t, "Consumer avro", res.Err)
	if len(res.Results) == 0 {
		t.Fatal("no avro messages consumed")
	}
	val := res.Results[0].(map[string]any)["Value"].(string)
	if !strings.Contains(val, `"name":"hello"`) {
		t.Fatalf("decoded avro value unexpected: %s", val)
	}

	// 删除 subject
	del := s.DeleteSRSubject("topic-avro-value", false)
	mustOk(t, "DeleteSRSubject", del.Err)
}

func TestFakeUnsupportedMechanism(t *testing.T) {
	c, err := kfake.NewCluster(kfake.NumBrokers(1))
	if err != nil {
		t.Fatal(err)
	}
	defer c.Close()
	s := NewKafkaService()
	res := s.SetConnect("bad", map[string]any{
		"bootstrap_servers": strings.Join(c.ListenAddrs(), ","),
		"sasl":              "enable",
		"sasl_mechanism":    "NOT-A-MECH",
	}, true)
	if res.Err == "" {
		t.Fatal("expected unsupported mechanism error")
	}
	if !strings.Contains(res.Err, "unsupported SASL mechanism") {
		t.Fatalf("unexpected error: %s", res.Err)
	}
}

func TestFakeOauthAndMskValidation(t *testing.T) {
	c, err := kfake.NewCluster(kfake.NumBrokers(1))
	if err != nil {
		t.Fatal(err)
	}
	defer c.Close()
	s := NewKafkaService()
	addr := strings.Join(c.ListenAddrs(), ",")

	// OAUTHBEARER 缺 token 应报错
	res := s.SetConnect("oauth", map[string]any{
		"bootstrap_servers": addr,
		"sasl":              "enable",
		"sasl_mechanism":    "OAUTHBEARER",
		"sasl_user":         "",
		"sasl_pwd":          "",
	}, true)
	if res.Err == "" || !strings.Contains(res.Err, "OAUTHBEARER") {
		t.Fatalf("expected oauth token error, got: %s", res.Err)
	}

	// MSK IAM 未开 TLS 应报错
	res = s.SetConnect("msk", map[string]any{
		"bootstrap_servers": addr,
		"sasl":              "enable",
		"sasl_mechanism":    "AWS_MSK_IAM",
		"sasl_user":         "AK",
		"sasl_pwd":          "SK",
	}, true)
	if res.Err == "" || !strings.Contains(res.Err, "TLS") {
		t.Fatalf("expected msk tls error, got: %s", res.Err)
	}
}
