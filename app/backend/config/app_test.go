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
	"app/backend/types"
	"os"
	"path/filepath"
	"testing"
)

// newTestApp 把配置目录重定向到临时目录，避免测试读写真实的 ~/.kafka-king
func newTestApp(t *testing.T) *AppConfig {
	t.Helper()
	home := t.TempDir()
	// os.UserHomeDir: Unix 读 HOME，Windows 读 USERPROFILE，都指到临时目录
	t.Setenv("HOME", home)
	t.Setenv("USERPROFILE", home)
	return &AppConfig{}
}

func TestExportImportConnects(t *testing.T) {
	a := newTestApp(t)

	cfg := &types.Config{
		Width:  1248,
		Height: 768,
		Theme:  "darkTheme",
		Connects: []types.Connect{
			{Id: 1, Name: "prod", BootstrapServers: "b1:9092,b2:9092", Sasl: "enable", SaslMechanism: "SCRAM-SHA-512", SaslUser: "u", SaslPwd: "p", SaslSessionToken: "token123", UseKerberos: "enable"},
			{Id: 2, Name: "dev", BootstrapServers: "localhost:9092"},
		},
	}
	if errStr := a.SaveConfig(cfg); errStr != "" {
		t.Fatalf("SaveConfig failed: %s", errStr)
	}

	// 导出
	exportPath := filepath.Join(t.TempDir(), "conns.yaml")
	res := a.ExportConnects(exportPath)
	if res.Err != "" {
		t.Fatalf("ExportConnects failed: %s", res.Err)
	}
	if got := res.Result["count"].(int); got != 2 {
		t.Fatalf("export count = %d, want 2", got)
	}
	if _, err := os.Stat(exportPath); err != nil {
		t.Fatalf("export file missing: %v", err)
	}

	// 清空后导入（跳过模式）
	if errStr := a.SaveConfig(&types.Config{Connects: []types.Connect{}}); errStr != "" {
		t.Fatalf("SaveConfig failed: %s", errStr)
	}
	res = a.ImportConnects(exportPath, false)
	if res.Err != "" {
		t.Fatalf("ImportConnects failed: %s", res.Err)
	}
	if res.Result["imported"].(int) != 2 || res.Result["skipped"].(int) != 0 {
		t.Fatalf("import result = %+v, want imported=2 skipped=0", res.Result)
	}
	got := a.GetConfig()
	if len(got.Connects) != 2 {
		t.Fatalf("after import connects = %d, want 2", len(got.Connects))
	}
	var prod *types.Connect
	for i := range got.Connects {
		if got.Connects[i].Name == "prod" {
			prod = &got.Connects[i]
		}
	}
	if prod == nil || prod.SaslPwd != "p" || prod.BootstrapServers != "b1:9092,b2:9092" || prod.SaslSessionToken != "token123" || prod.UseKerberos != "enable" {
		t.Fatalf("imported prod conn fields lost: %+v", prod)
	}

	// 再次导入：跳过模式下应全部 skipped，不产生重复
	res = a.ImportConnects(exportPath, false)
	if res.Result["imported"].(int) != 0 || res.Result["skipped"].(int) != 2 {
		t.Fatalf("second import result = %+v, want imported=0 skipped=2", res.Result)
	}
	if len(a.GetConfig().Connects) != 2 {
		t.Fatalf("duplicate connections created: %d", len(a.GetConfig().Connects))
	}

	// 覆盖模式：同名被更新
	cfg.Connects[1].BootstrapServers = "localhost:9093"
	if errStr := a.SaveConfig(cfg); errStr != "" {
		t.Fatalf("SaveConfig failed: %s", errStr)
	}
	res = a.ImportConnects(exportPath, true)
	if res.Result["updated"].(int) != 2 {
		t.Fatalf("overwrite import result = %+v, want updated=2", res.Result)
	}
	for _, c := range a.GetConfig().Connects {
		if c.Name == "dev" && c.BootstrapServers != "localhost:9092" {
			t.Fatalf("overwrite import did not restore dev conn: %+v", c)
		}
	}
}

func TestImportConnectsBadFile(t *testing.T) {
	a := newTestApp(t)
	dir := t.TempDir()

	// 不存在的文件
	if res := a.ImportConnects(filepath.Join(dir, "nope.yaml"), true); res.Err == "" {
		t.Fatal("expected error for missing file")
	}
	// 非 connects 格式
	bad := filepath.Join(dir, "bad.yaml")
	if err := os.WriteFile(bad, []byte("foo: bar\n"), 0644); err != nil {
		t.Fatal(err)
	}
	if res := a.ImportConnects(bad, true); res.Err == "" {
		t.Fatal("expected error for file without connects list")
	}
}
