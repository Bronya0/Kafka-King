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

package system

import (
	"app/backend/common"
	"app/backend/types"
	"context"
	"fmt"
	"github.com/go-resty/resty/v2"
	"runtime"
	"runtime/debug"
	"strings"
	"time"
)

type Update struct {
	ctx context.Context
}

func (obj *Update) Start(ctx context.Context) {
	obj.ctx = ctx
}
func (obj *Update) CheckUpdate() *types.Tag {
	client := resty.New().SetTimeout(10 * time.Second)
	tag := &types.Tag{}
	resp, err := client.R().SetResult(tag).Get(common.UPDATE_URL)
	if err != nil || resp.StatusCode() != 200 {
		return nil
	}
	tag.TagName = strings.TrimSpace(tag.TagName)
	return tag
}

func (obj *Update) GetProcessInfo() string {
	// 获取内存统计信息
	var memStats runtime.MemStats
	runtime.ReadMemStats(&memStats)

	// 获取构建信息
	var goVersion string
	if buildInfo, ok := debug.ReadBuildInfo(); ok {
		goVersion = buildInfo.GoVersion
	} else {
		goVersion = runtime.Version()
	}

	// 格式化输出详细信息
	info := fmt.Sprintf(
		"Basic Information:\n"+
			"- Go Version: %s\n"+
			"- Operating System: %s\n"+
			"- Architecture: %s\n"+
			"- Number of CPUs: %d\n"+
			"- Number of Goroutines: %d\n"+
			"- Current Timestamp: %s\n\n"+
			"Memory Statistics:\n"+
			"- Allocated Memory: %.2f MB\n"+
			"- Total Allocated Memory: %.2f MB\n"+
			"- System Memory: %.2f MB\n"+
			"- Heap Allocated: %.2f MB\n"+
			"- Heap System Memory: %.2f MB\n"+
			"- Heap Idle: %.2f MB\n"+
			"- Heap In Use: %.2f MB\n"+
			"- Stack In Use: %.2f MB\n"+
			"- Number of Heap Objects: %d\n"+
			"- Memory Allocation Count: %d\n"+
			"- Memory Free Count: %d\n\n"+
			"Garbage Collection Statistics:\n"+
			"- Number of GC Runs: %d\n"+
			"- Last GC Time: %s\n"+
			"- Next GC Limit: %.2f MB\n"+
			"- GC CPU Fraction: %.4f%%\n"+
			"- Total GC Pause Time: %v\n",
		goVersion,                        // Go版本
		runtime.GOOS,                     // 操作系统
		runtime.GOARCH,                   // 体系结构
		runtime.NumCPU(),                 // CPU数量
		runtime.NumGoroutine(),           // 协程数量
		time.Now().Format(time.DateTime), // 当前时间戳

		float64(memStats.Alloc)/1024/1024,      // 已分配内存
		float64(memStats.TotalAlloc)/1024/1024, // 总分配内存
		float64(memStats.Sys)/1024/1024,        // 系统内存
		float64(memStats.HeapAlloc)/1024/1024,  // 堆分配
		float64(memStats.HeapSys)/1024/1024,    // 堆系统内存
		float64(memStats.HeapIdle)/1024/1024,   // 堆空闲
		float64(memStats.HeapInuse)/1024/1024,  // 堆使用中
		float64(memStats.StackInuse)/1024/1024, // 栈使用中
		memStats.HeapObjects,                   // 堆对象数量
		memStats.Mallocs,                       // 内存分配次数
		memStats.Frees,                         // 内存释放次数

		memStats.NumGC, // 垃圾回收运行次数
		time.Unix(0, int64(memStats.LastGC)).Format(time.DateTime), // 上次垃圾回收时间
		float64(memStats.NextGC)/1024/1024,                         // 下次垃圾回收限制
		memStats.GCCPUFraction*100,                                 // 垃圾回收CPU占比
		time.Duration(memStats.PauseTotalNs),                       // 垃圾回收总暂停时间
	)

	return info
}
