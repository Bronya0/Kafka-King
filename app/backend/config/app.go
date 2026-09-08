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

package config

import (
	"app/backend/common"
	"app/backend/types"
	"context"
	"fmt"
	"github.com/wailsapp/wails/v2/pkg/runtime"
	"gopkg.in/yaml.v3"
	"log"
	"os"
	"path/filepath"
	"sync"
)

type AppConfig struct {
	ctx context.Context
	mu  sync.Mutex
}

func (a *AppConfig) Start(ctx context.Context) {
	a.ctx = ctx
}

func (a *AppConfig) GetConfig() *types.Config {
	a.mu.Lock()
	defer a.mu.Unlock()
	return a.getConfigLocked()
}

// getConfigLocked 读取配置文件，要求调用方已持有 a.mu。
func (a *AppConfig) getConfigLocked() *types.Config {
	var defaultConfig = &types.Config{
		Width:    common.Width,
		Height:   common.Height,
		Theme:    common.Theme,
		Connects: make([]types.Connect, 0),
	}
	configPath := a.getConfigPath()
	data, err := os.ReadFile(configPath)
	if err != nil {
		return defaultConfig
	}
	err = yaml.Unmarshal(data, defaultConfig)
	if err != nil {
		return defaultConfig
	}
	fmt.Println("config", defaultConfig)
	return defaultConfig
}

func (a *AppConfig) SaveConfig(config *types.Config) string {
	a.mu.Lock()
	defer a.mu.Unlock()
	configPath := a.getConfigPath()
	fmt.Println(configPath)
	return a.writeConfigLocked(configPath, config)
}
func (a *AppConfig) SaveTheme(theme string) string {
	a.mu.Lock()
	defer a.mu.Unlock()
	config := a.getConfigLocked()
	config.Theme = theme
	return a.writeConfigLocked(a.getConfigPath(), config)
}

// writeConfigLocked 序列化并落盘，要求调用方已持有 a.mu。
func (a *AppConfig) writeConfigLocked(configPath string, config *types.Config) string {
	data, err := yaml.Marshal(config)
	if err != nil {
		return err.Error()
	}
	if err := os.WriteFile(configPath, data, 0644); err != nil {
		return err.Error()
	}
	return ""
}

// connectsFile 连接配置导出/导入文件的格式：只包含连接，不含窗口等本机配置。
type connectsFile struct {
	Connects []types.Connect `yaml:"connects"`
}

// ExportConnects 将已保存的全部连接导出到 path（YAML）。无扩展名时自动补 .yaml。
func (a *AppConfig) ExportConnects(path string) *types.ResultResp {
	result := &types.ResultResp{}
	if path == "" {
		result.Err = "path is required"
		return result
	}
	if filepath.Ext(path) == "" {
		path += ".yaml"
	}

	a.mu.Lock()
	defer a.mu.Unlock()
	cfg := a.getConfigLocked()
	data, err := yaml.Marshal(connectsFile{Connects: cfg.Connects})
	if err != nil {
		result.Err = err.Error()
		return result
	}
	if err := os.WriteFile(path, data, 0644); err != nil {
		result.Err = err.Error()
		return result
	}
	result.Result = map[string]any{"count": len(cfg.Connects), "path": path}
	return result
}

// ImportConnects 从 path 导入连接（YAML 或 JSON，yaml 是 json 超集均可解析）。
// overwrite 为 true 时同名连接被覆盖（保留原 id），否则跳过；新增连接自动分配 id。
func (a *AppConfig) ImportConnects(path string, overwrite bool) *types.ResultResp {
	result := &types.ResultResp{}
	if path == "" {
		result.Err = "path is required"
		return result
	}
	data, err := os.ReadFile(path)
	if err != nil {
		result.Err = err.Error()
		return result
	}
	var file connectsFile
	if err := yaml.Unmarshal(data, &file); err != nil {
		result.Err = err.Error()
		return result
	}
	if len(file.Connects) == 0 {
		result.Err = "no connections found in file (expect a `connects` list)"
		return result
	}

	a.mu.Lock()
	defer a.mu.Unlock()
	cfg := a.getConfigLocked()

	index := make(map[string]int, len(cfg.Connects))
	maxID := 0
	for i, c := range cfg.Connects {
		index[c.Name] = i
		if c.Id > maxID {
			maxID = c.Id
		}
	}

	imported, updated, skipped := 0, 0, 0
	for _, c := range file.Connects {
		// 过滤脏数据：无名字或无地址的连接不导入
		if c.Name == "" || c.BootstrapServers == "" {
			skipped++
			continue
		}
		if idx, ok := index[c.Name]; ok {
			if !overwrite {
				skipped++
				continue
			}
			c.Id = cfg.Connects[idx].Id // 保留本地 id，前端编辑/删除依赖它
			cfg.Connects[idx] = c
			updated++
		} else {
			maxID++
			c.Id = maxID
			cfg.Connects = append(cfg.Connects, c)
			index[c.Name] = len(cfg.Connects) - 1
			imported++
		}
	}

	if errStr := a.writeConfigLocked(a.getConfigPath(), cfg); errStr != "" {
		result.Err = errStr
		return result
	}
	result.Result = map[string]any{
		"imported": imported,
		"updated":  updated,
		"skipped":  skipped,
		"total":    len(cfg.Connects),
	}
	return result
}

func (a *AppConfig) getConfigPath() string {
	homeDir, err := os.UserHomeDir()
	if err != nil {
		log.Printf("os.UserHomeDir() error: %s", err.Error())
		return common.ConfigPath
	}
	configDir := filepath.Join(homeDir, common.ConfigDir)
	_, err = os.Stat(configDir)
	if os.IsNotExist(err) {
		err = os.Mkdir(configDir, os.ModePerm)
		if err != nil {
			log.Printf("create configDir %s error: %s", configDir, err.Error())
			return common.ConfigPath
		}
	}
	return filepath.Join(configDir, common.ConfigPath)
}

// GetVersion returns the application version
func (a *AppConfig) GetVersion() string {
	return common.Version
}

func (a *AppConfig) GetAppName() string {
	return common.AppName
}

func (a *AppConfig) OpenFileDialog(options runtime.OpenDialogOptions) (string, error) {
	return runtime.OpenFileDialog(a.ctx, options)
}

func (a *AppConfig) SaveFileDialog(options runtime.SaveDialogOptions) (string, error) {
	return runtime.SaveFileDialog(a.ctx, options)
}
func (a *AppConfig) LogErrToFile(message string) {
	file, err := os.OpenFile(common.ErrLogPath, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Println("Failed to open log file:", err)
		return
	}
	defer file.Close()

	if _, err := file.WriteString(message); err != nil {
		log.Println("Failed to write to log file:", err)
	}
}
