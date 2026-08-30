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
	"sort"
	"time"

	"github.com/twmb/franz-go/pkg/kadm"
	"github.com/twmb/franz-go/pkg/kerr"
	"github.com/twmb/franz-go/pkg/kmsg"
)

// GetLogDirs 描述所有 broker 的日志目录及各分区占用大小。
// 返回 dirs：每个 broker 每个目录的汇总；partitions：每个 topic 分区的明细。
func (k *Service) GetLogDirs() *types.ResultResp {
	result := &types.ResultResp{}
	if k.kac == nil {
		result.Err = common.PleaseSelectErr
		return result
	}
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	all, err := k.kac.DescribeAllLogDirs(ctx, nil)
	if err != nil {
		result.Err = "DescribeAllLogDirs Error：" + err.Error()
		return result
	}

	dirs := make([]any, 0)
	partitions := make([]any, 0)
	for _, d := range all.Sorted() {
		if d.Err != nil {
			dirs = append(dirs, map[string]any{
				"broker": d.Broker,
				"dir":    d.Dir,
				"err":    d.Err.Error(),
			})
			continue
		}
		dirs = append(dirs, map[string]any{
			"broker": d.Broker,
			"dir":    d.Dir,
			"size":   d.Size(),
			"err":    "",
		})
		for t, ps := range d.Topics {
			for p, dp := range ps {
				partitions = append(partitions, map[string]any{
					"broker":     dp.Broker,
					"dir":        dp.Dir,
					"topic":      t,
					"partition":  p,
					"size":       dp.Size,
					"offset_lag": dp.OffsetLag,
				})
			}
		}
	}
	sort.Slice(partitions, func(i, j int) bool {
		a := partitions[i].(map[string]any)
		b := partitions[j].(map[string]any)
		return a["size"].(int64) > b["size"].(int64)
	})
	result.Result = map[string]any{
		"dirs":       dirs,
		"partitions": partitions,
	}
	return result
}

// ListReassignments 查询正在进行的分区副本重分配。
func (k *Service) ListReassignments(topics []string) *types.ResultResp {
	result := &types.ResultResp{}
	if k.kac == nil {
		result.Err = common.PleaseSelectErr
		return result
	}
	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()

	var s kadm.TopicsSet
	for _, t := range topics {
		s.Add(t)
	}
	resps, err := k.kac.ListPartitionReassignments(ctx, s)
	if err != nil {
		result.Err = "ListPartitionReassignments Error：" + err.Error()
		return result
	}
	reassigning := make([]any, 0)
	for _, r := range resps.Sorted() {
		reassigning = append(reassigning, map[string]any{
			"topic":     r.Topic,
			"partition": r.Partition,
			"replicas":  r.Replicas,
			"adding":    r.AddingReplicas,
			"removing":  r.RemovingReplicas,
		})
	}
	result.Result = map[string]any{"reassignments": reassigning}
	return result
}

// AlterPartitionReassignments 为 topic 的指定分区设置新的副本分布。
// assignments 形如 {"0":[1,2], "1":[2,3]}；replicas 为 null/空表示取消该分区的进行中重分配。
func (k *Service) AlterPartitionReassignments(topic string, assignments map[string][]int32) *types.ResultResp {
	result := &types.ResultResp{}
	if k.kac == nil {
		result.Err = common.PleaseSelectErr
		return result
	}
	if topic == "" {
		result.Err = "topic is required"
		return result
	}
	if len(assignments) == 0 {
		result.Err = "assignments is empty"
		return result
	}

	req := kmsg.NewPtrAlterPartitionAssignmentsRequest()
	req.TimeoutMillis = 30000
	rt := kmsg.NewAlterPartitionAssignmentsRequestTopic()
	rt.Topic = topic
	for p, replicas := range assignments {
		partition := int32(0)
		if _, err := fmt.Sscanf(p, "%d", &partition); err != nil {
			result.Err = fmt.Sprintf("invalid partition key %q", p)
			return result
		}
		rp := kmsg.NewAlterPartitionAssignmentsRequestTopicPartition()
		rp.Partition = partition
		if len(replicas) > 0 {
			rp.Replicas = replicas
		} else {
			// nil 表示取消进行中的重分配
			rp.Replicas = nil
		}
		rt.Partitions = append(rt.Partitions, rp)
	}
	req.Topics = append(req.Topics, rt)

	ctx, cancel := context.WithTimeout(context.Background(), 45*time.Second)
	defer cancel()
	resp, err := k.client.Request(ctx, req)
	if err != nil {
		result.Err = "AlterPartitionReassignments Error：" + err.Error()
		return result
	}
	rres, ok := resp.(*kmsg.AlterPartitionAssignmentsResponse)
	if !ok {
		result.Err = "unexpected response type"
		return result
	}
	if rres.ErrorCode != 0 {
		result.Err = fmt.Sprintf("AlterPartitionReassignments Error: %s", kerrString(rres.ErrorCode, rres.ErrorMessage))
		return result
	}
	for _, t := range rres.Topics {
		for _, p := range t.Partitions {
			if p.ErrorCode != 0 {
				result.Err = fmt.Sprintf("topic %s partition %d: %s", t.Topic, p.Partition, kerrString(p.ErrorCode, p.ErrorMessage))
			}
		}
	}
	return result
}

func kerrString(code int16, msg *string) string {
	if err := kerr.ErrorForCode(code); err != nil {
		if msg != nil && *msg != "" {
			return fmt.Sprintf("%v (%s)", err, *msg)
		}
		return err.Error()
	}
	if msg != nil {
		return *msg
	}
	return fmt.Sprintf("error code %d", code)
}

// GetQuotas 查询所有客户端配额。
func (k *Service) GetQuotas() *types.ResultsResp {
	result := &types.ResultsResp{Results: make([]any, 0)}
	if k.kac == nil {
		result.Err = common.PleaseSelectErr
		return result
	}
	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()

	// strict=false, 组件为空 => 匹配所有实体
	quotas, err := k.kac.DescribeClientQuotas(ctx, false, nil)
	if err != nil {
		result.Err = "DescribeClientQuotas Error：" + err.Error()
		return result
	}
	for _, q := range quotas {
		values := map[string]float64{}
		for _, v := range q.Values {
			values[v.Key] = v.Value
		}
		result.Results = append(result.Results, map[string]any{
			"entity": q.Entity.String(),
			"values": values,
		})
	}
	return result
}

// AlterQuota 新增/修改/删除配额。
// entityType: user / client-id / ip；entityName 为空表示默认实体；
// ops: [{"key":"producer_byte_rate","value":102400,"remove":false}, ...]
func (k *Service) AlterQuota(entityType string, entityName string, ops []map[string]any) *types.ResultResp {
	result := &types.ResultResp{}
	if k.kac == nil {
		result.Err = common.PleaseSelectErr
		return result
	}
	if entityType == "" {
		result.Err = "entity type is required"
		return result
	}
	if len(ops) == 0 {
		result.Err = "ops is empty"
		return result
	}

	entry := kadm.AlterClientQuotaEntry{}
	name := entityName
	var namePtr *string
	if name != "" {
		namePtr = &name
	}
	entry.Entity = kadm.ClientQuotaEntity{
		{Type: entityType, Name: namePtr},
	}
	for _, op := range ops {
		key, _ := op["key"].(string)
		if key == "" {
			result.Err = "quota key is required"
			return result
		}
		ao := kadm.AlterClientQuotaOp{Key: key}
		if remove, ok := op["remove"].(bool); ok && remove {
			ao.Remove = true
		} else {
			var val float64
			switch v := op["value"].(type) {
			case float64:
				val = v
			case int:
				val = float64(v)
			case int64:
				val = float64(v)
			default:
				result.Err = fmt.Sprintf("invalid quota value for %s", key)
				return result
			}
			ao.Value = val
		}
		entry.Ops = append(entry.Ops, ao)
	}

	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()
	altered, err := k.kac.AlterClientQuotas(ctx, []kadm.AlterClientQuotaEntry{entry})
	if err != nil {
		result.Err = "AlterClientQuotas Error：" + err.Error()
		return result
	}
	for _, a := range altered {
		if a.Err != nil {
			result.Err = fmt.Sprintf("alter quota failed: %v", a.Err)
			return result
		}
	}
	return result
}
