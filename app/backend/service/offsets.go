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
	"app/backend/common"
	"app/backend/types"
	"context"
	"fmt"
	"strings"
	"time"

	"github.com/twmb/franz-go/pkg/kadm"
)

// ResetGroupOffsets 重置消费组的已提交 offset。
//
// strategy:
//   - "start":    每个分区重置到最早
//   - "end":      每个分区重置到最晚
//   - "timestamp": 重置到大于给定时间戳（毫秒）的第一条消息
//   - "absolute": 所有分区重置到 value 指定的同一 offset
//
// topics 为空时自动使用该 group 已提交过的所有 topic。
// 注意：若 group 仍有活跃成员，broker 会拒绝提交（需要先停止消费者）。
func (k *Service) ResetGroupOffsets(group string, topics []string, strategy string, value int64) *types.ResultResp {
	result := &types.ResultResp{}
	if k.kac == nil {
		result.Err = common.PleaseSelectErr
		return result
	}
	if group == "" {
		result.Err = "group is required"
		return result
	}

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// 本应用占用的该 group 的消费者先断开，否则 broker 会拒绝提交（UNKNOWN_MEMBER_ID/ILLEGAL_GENERATION）
	k.CloseAllStreams()
	k.mutex.Lock()
	if k.oneShot != nil && k.oneShot.client != nil {
		k.oneShot.client.Close()
		k.oneShot = nil
	}
	k.mutex.Unlock()

	// 未指定 topics：用该 group 已提交过的 offsets 推断 topic 列表
	if len(topics) == 0 {
		fetched, err := k.kac.FetchOffsets(ctx, group)
		if err != nil {
			result.Err = "FetchOffsets Error：" + err.Error()
			return result
		}
		seen := map[string]bool{}
		for _, o := range fetched.Sorted() {
			if o.Topic != "" && !seen[o.Topic] {
				seen[o.Topic] = true
				topics = append(topics, o.Topic)
			}
		}
		if len(topics) == 0 {
			result.Err = "no committed topics found for group " + group
			return result
		}
	}

	var target kadm.Offsets
	switch strings.ToLower(strategy) {
	case "start":
		listed, err := k.kac.ListStartOffsets(ctx, topics...)
		if err != nil {
			result.Err = "ListStartOffsets Error：" + err.Error()
			return result
		}
		target = listed.Offsets()
	case "end":
		listed, err := k.kac.ListEndOffsets(ctx, topics...)
		if err != nil {
			result.Err = "ListEndOffsets Error：" + err.Error()
			return result
		}
		target = listed.Offsets()
	case "timestamp":
		if value <= 0 {
			result.Err = "timestamp must be positive milliseconds"
			return result
		}
		listed, err := k.kac.ListOffsetsAfterMilli(ctx, value, topics...)
		if err != nil {
			result.Err = "ListOffsetsAfterMilli Error：" + err.Error()
			return result
		}
		target = listed.Offsets()
	case "absolute":
		if value < 0 {
			result.Err = "offset must be >= 0"
			return result
		}
		target = kadm.Offsets{}
		ends, err := k.kac.ListEndOffsets(ctx, topics...)
		if err != nil {
			result.Err = "ListEndOffsets Error：" + err.Error()
			return result
		}
		ends.Each(func(l kadm.ListedOffset) {
			target.AddOffset(l.Topic, l.Partition, value, -1)
		})
	default:
		result.Err = fmt.Sprintf("unsupported reset strategy: %s", strategy)
		return result
	}

	committed, err := k.kac.CommitOffsets(ctx, group, target)
	if err != nil {
		result.Err = "CommitOffsets Error：" + err.Error()
		return result
	}
	for _, c := range committed.Sorted() {
		if c.Err != nil {
			result.Err = fmt.Sprintf("commit %s-%d failed: %v", c.Topic, c.Partition, c.Err)
			return result
		}
	}

	// 返回重置后的 offset 便于前端回显
	offsets := make([]any, 0)
	for _, o := range target.Sorted() {
		offsets = append(offsets, map[string]any{
			"topic":     o.Topic,
			"partition": o.Partition,
			"at":        o.At,
		})
	}
	result.Result = map[string]any{"offsets": offsets}
	return result
}

// DeleteRecords 删除 topic 在给定 offset 之前的所有记录（不可恢复！）。
// partitions 为空表示所有分区；offset 为每个分区删除的上界（不含）。
// offset 传 -1 表示删除各分区的全部已存在消息（以 ListEndOffsets 为准）。
func (k *Service) DeleteRecords(topic string, partitions []int32, offset int64) *types.ResultResp {
	result := &types.ResultResp{}
	if k.kac == nil {
		result.Err = common.PleaseSelectErr
		return result
	}
	if topic == "" {
		result.Err = "topic is required"
		return result
	}

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	os := kadm.Offsets{}
	if len(partitions) == 0 {
		// 全部分区：用 end offsets 确定分区集合
		ends, err := k.kac.ListEndOffsets(ctx, topic)
		if err != nil {
			result.Err = "ListEndOffsets Error：" + err.Error()
			return result
		}
		ends.Each(func(l kadm.ListedOffset) {
			at := offset
			if offset < 0 {
				at = l.Offset // 删除全部
			} else if at > l.Offset {
				// 目标 offset 超过分区水位（该分区消息不足），钳制为删除全部
				at = l.Offset
			}
			os.AddOffset(l.Topic, l.Partition, at, -1)
		})
	} else {
		ends, err := k.kac.ListEndOffsets(ctx, topic)
		if err != nil {
			result.Err = "ListEndOffsets Error：" + err.Error()
			return result
		}
		endByPartition := map[int32]int64{}
		ends.Each(func(l kadm.ListedOffset) {
			endByPartition[l.Partition] = l.Offset
		})
		for _, p := range partitions {
			at := offset
			if end, ok := endByPartition[p]; ok && at > end {
				at = end
			}
			os.AddOffset(topic, p, at, -1)
		}
	}

	resps, err := k.kac.DeleteRecords(ctx, os)
	if err != nil {
		result.Err = "DeleteRecords Error：" + err.Error()
		return result
	}
	deleted := make([]any, 0)
	resps.Each(func(r kadm.DeleteRecordsResponse) {
		if r.Err != nil {
			result.Err = fmt.Sprintf("delete %s-%d failed: %v", r.Topic, r.Partition, r.Err)
		}
		deleted = append(deleted, map[string]any{
			"topic":         r.Topic,
			"partition":     r.Partition,
			"low_watermark": r.LowWatermark, // 删除后的新起始 offset
		})
	})
	if result.Err != "" {
		return result
	}
	result.Result = map[string]any{"deleted": deleted}
	return result
}
