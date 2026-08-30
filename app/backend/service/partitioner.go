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
	"github.com/twmb/franz-go/pkg/kgo"
)

// autoPartitioner 兼容“显式指定分区”与“自动分配”两种模式：
// record.Partition >= 0 时直接使用该分区，否则退回 StickyKey（按 key hash，无 key 时粘性随机）。
// kgo 默认分区器会忽略 record 上已设置的分区，ManualPartitioner 又要求必须设置分区，
// 因此需要这个二合一实现。
type autoPartitioner struct {
	fallback kgo.Partitioner
}

func newAutoPartitioner() kgo.Partitioner {
	return &autoPartitioner{fallback: kgo.StickyKeyPartitioner(nil)}
}

func (p *autoPartitioner) ForTopic(t string) kgo.TopicPartitioner {
	return &autoTopicPartitioner{fallback: p.fallback.ForTopic(t)}
}

type autoTopicPartitioner struct {
	fallback kgo.TopicPartitioner
}

func (p *autoTopicPartitioner) Partition(r *kgo.Record, numPartitions int) int {
	if r.Partition >= 0 && int(r.Partition) < numPartitions {
		return int(r.Partition)
	}
	return p.fallback.Partition(r, numPartitions)
}

func (p *autoTopicPartitioner) RequiresConsistency(r *kgo.Record) bool {
	return p.fallback.RequiresConsistency(r)
}
