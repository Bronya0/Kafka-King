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
	"app/backend/utils/compress"
	"context"
	"errors"
	"fmt"
	"log"
	"strings"
	"time"

	"github.com/google/uuid"
	"github.com/twmb/franz-go/pkg/kgo"
	"github.com/wailsapp/wails/v2/pkg/runtime"
)

// StreamInstance 一路独立的流式消费。每一路拥有自己的 kgo.Client，
// 互不干扰，可同时存在多个。
type StreamInstance struct {
	ID      string `json:"id"`
	Topic   string `json:"topic"`
	Group   string `json:"group"`
	Running bool   `json:"running"`

	cancel context.CancelFunc
	client *kgo.Client
	ended  bool // consumer-end 是否已发出，避免重复
}

// streamMsgEvent / streamErrEvent 是推送给前端的事件结构
type streamMsgEvent struct {
	ID   string `json:"id"`
	Rows []any  `json:"rows"`
}

type streamErrEvent struct {
	ID  string `json:"id"`
	Err string `json:"err"`
}

type streamEndEvent struct {
	ID string `json:"id"`
}

// testEventHook 测试钩子：非 nil 时事件不发送给 Wails 前端，而是交给测试收集。
var testEventHook func(name string, data any)

// emitEvent 安全地向 Wails 前端发送事件。
// 在非 Wails 环境（单元测试）下 EventsEmit 会 panic，这里统一 recover，
// 并在有测试钩子时转发给测试。
func (k *Service) emitEvent(name string, data any) {
	if testEventHook != nil {
		testEventHook(name, data)
		return
	}
	defer func() { _ = recover() }() // 非运行时 context 下忽略 panic
	if k.appCtx == nil {
		return
	}
	runtime.EventsEmit(k.appCtx, name, data)
}

// GetStreamState 返回所有流的状态列表
func (k *Service) GetStreamState() *types.ResultResp {
	result := &types.ResultResp{}
	k.mutex.Lock()
	defer k.mutex.Unlock()

	streams := make([]any, 0, len(k.streams))
	for _, s := range k.streams {
		streams = append(streams, map[string]any{
			"id":      s.ID,
			"topic":   s.Topic,
			"group":   s.Group,
			"running": s.Running,
		})
	}
	result.Result = map[string]any{"streams": streams}
	return result
}

// StopStreamConsumer 停止流式消费。id 为空时停止所有流。
func (k *Service) StopStreamConsumer(id string) *types.ResultResp {
	result := &types.ResultResp{}

	k.mutex.Lock()
	toStop := make([]*StreamInstance, 0, len(k.streams))
	for key, s := range k.streams {
		if id == "" || key == id {
			toStop = append(toStop, s)
			delete(k.streams, key)
		}
	}
	k.mutex.Unlock()

	for _, s := range toStop {
		k.stopStreamInstance(s)
	}
	return result
}

func (k *Service) stopStreamInstance(s *StreamInstance) {
	k.mutex.Lock()
	already := s.ended
	s.ended = true
	k.mutex.Unlock()
	if s.cancel != nil {
		s.cancel()
	}
	if s.client != nil {
		s.client.Close()
	}
	if !already {
		k.emitEvent("consumer-end", streamEndEvent{ID: s.ID})
	}
}

// StartStreamConsumer 启动一路流式消费。
// streamID 由前端生成；为空则自动生成。相同 ID 的已有流会被先停止（替换语义）。
// startOffset > 0 时按该 offset 起始（对所有分区生效），优先级高于 isLatest/startTimestamp。
func (k *Service) StartStreamConsumer(streamID string, topic string, group string, num int, timeout int, decompress string, isolationLevel string, isCommit bool, isLatest bool, startTimestamp int, startOffset int64, decode string) *types.ResultResp {
	result := &types.ResultResp{}

	// 流式消费批量拉取，减少 IPC 批次数；至少取 10000 条
	const streamBatchSize = 10000
	if num < streamBatchSize {
		num = streamBatchSize
	}

	if k.kac == nil {
		result.Err = common.PleaseSelectErr
		return result
	}
	if topic == "" {
		result.Err = "topic is required"
		return result
	}
	if group == "" {
		group = "__kafka_king_auto_generate__"
	}
	if streamID == "" {
		streamID = uuid.NewString()
	}

	// 替换同 ID 的旧流
	k.mutex.Lock()
	old, hadOld := k.streams[streamID]
	if hadOld {
		delete(k.streams, streamID)
	}

	cl, err := k.newConsumerClient(topic, group, isolationLevel, isLatest, startTimestamp, startOffset)
	if err != nil {
		k.mutex.Unlock()
		if hadOld {
			k.stopStreamInstance(old)
		}
		result.Err = "Consumer Error：" + err.Error()
		return result
	}

	streamCtx, cancel := context.WithCancel(context.Background())
	inst := &StreamInstance{
		ID:      streamID,
		Topic:   topic,
		Group:   group,
		Running: true,
		cancel:  cancel,
		client:  cl,
	}
	k.streams[streamID] = inst
	k.mutex.Unlock()
	if hadOld {
		k.stopStreamInstance(old)
	}

	go k.streamLoop(inst, streamCtx, num, timeout, decompress, decode, isCommit)

	k.emitEvent("consumer-start", map[string]any{
		"id":    streamID,
		"topic": topic,
		"group": group,
	})
	result.Result = map[string]any{"id": streamID}
	return result
}

// streamLoop 是流式消费的 poll 循环，在独立 goroutine 中运行。
func (k *Service) streamLoop(inst *StreamInstance, streamCtx context.Context, num int, timeout int, decompress string, decode string, isCommit bool) {
	defer func() {
		if r := recover(); r != nil {
			log.Printf("stream consumer %s panic: %v", inst.ID, r)
		}
		inst.Running = false
		// 从注册表中移除自己（若未被替换）
		k.mutex.Lock()
		if cur, ok := k.streams[inst.ID]; ok && cur == inst {
			delete(k.streams, inst.ID)
		}
		already := inst.ended
		inst.ended = true
		k.mutex.Unlock()
		if !already {
			k.emitEvent("consumer-end", streamEndEvent{ID: inst.ID})
		}
	}()

	if timeout <= 0 {
		timeout = 5
	}

	for {
		select {
		case <-streamCtx.Done():
			return
		default:
		}

		ctx, cancel2 := context.WithTimeout(streamCtx, time.Duration(timeout)*time.Second)
		fetches := inst.client.PollRecords(ctx, num)
		cancel2()

		if streamCtx.Err() != nil {
			return
		}

		if fetches.IsClientClosed() {
			k.emitEvent("consumer-err", streamErrEvent{ID: inst.ID, Err: "Client Closed, Please Retry"})
			return
		}

		if errs := fetches.Errors(); len(errs) > 0 {
			filtered := make([]string, 0, len(errs))
			for _, e := range errs {
				if errors.Is(e.Err, context.DeadlineExceeded) || errors.Is(e.Err, context.Canceled) {
					continue
				}
				filtered = append(filtered, e.Err.Error())
			}
			if len(filtered) > 0 {
				k.emitEvent("consumer-err", streamErrEvent{ID: inst.ID, Err: strings.Join(filtered, "; ")})
			}
		}

		records := fetches.Records()
		if len(records) > 0 {
			rows := make([]any, 0, len(records))
			for _, v := range records {
				if v == nil {
					continue
				}
				row, err := k.buildMessageRow(v, decompress, decode)
				if err != nil {
					log.Printf("stream consumer %s build row failed for offset %d: %v", inst.ID, v.Offset, err)
					continue
				}
				rows = append(rows, row)
			}
			if len(rows) > 0 {
				k.emitEvent("consumer-msg", streamMsgEvent{ID: inst.ID, Rows: rows})
			}
			if isCommit {
				if err := inst.client.CommitUncommittedOffsets(context.Background()); err != nil {
					log.Printf("stream consumer %s commit offsets failed: %v", inst.ID, err)
				}
			}
		}
	}
}

// buildMessageRow 将 kgo.Record 转成给前端的 map，含解压与解码逻辑。
func (k *Service) buildMessageRow(v *kgo.Record, decompress string, decode string) (map[string]any, error) {
	var data []byte
	var err error
	switch decompress {
	case "gzip":
		data, err = compress.GzipDecompress(v.Value)
	case "lz4":
		data, err = compress.Lz4Decompress(v.Value)
	case "zstd":
		data, err = compress.ZstdDecompress(v.Value)
	case "snappy":
		data, err = compress.SnappyDecompress(v.Value)
	default:
		data = v.Value
	}
	if err != nil {
		return nil, fmt.Errorf("decompress failed: %w", err)
	}

	valueStr, err := k.decodeValue(data, decode)
	if err != nil {
		return nil, err
	}

	return map[string]any{
		"Offset":        v.Offset,
		"Key":           string(v.Key),
		"Value":         valueStr,
		"Timestamp":     v.Timestamp.Format(time.DateTime),
		"Partition":     v.Partition,
		"Topic":         v.Topic,
		"Headers":       getHeadersString(v.Headers),
		"LeaderEpoch":   v.LeaderEpoch,
		"ProducerEpoch": v.ProducerEpoch,
		"ProducerID":    v.ProducerID,
	}, nil
}

// CloseAllStreams 停止全部流（自行加锁）。
func (k *Service) CloseAllStreams() {
	k.mutex.Lock()
	defer k.mutex.Unlock()
	k.stopAllStreamsLocked()
}

// stopAllStreamsLocked 在已持有 k.mutex 时停止全部流。
func (k *Service) stopAllStreamsLocked() {
	streams := make([]*StreamInstance, 0, len(k.streams))
	for key, s := range k.streams {
		streams = append(streams, s)
		delete(k.streams, key)
	}
	for _, s := range streams {
		already := s.ended
		s.ended = true
		if s.cancel != nil {
			s.cancel()
		}
		if s.client != nil {
			s.client.Close()
		}
		if !already {
			k.emitEvent("consumer-end", streamEndEvent{ID: s.ID})
		}
	}
}
