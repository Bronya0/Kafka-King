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

package main

import (
	"app/backend"
	"app/backend/common"
	"app/backend/config"
	"app/backend/service"
	"app/backend/system"
	"context"
	"embed"
	"fmt"

	"github.com/wailsapp/wails/v2"
	"github.com/wailsapp/wails/v2/pkg/options"
	"github.com/wailsapp/wails/v2/pkg/options/assetserver"
	"github.com/wailsapp/wails/v2/pkg/options/linux"
	"github.com/wailsapp/wails/v2/pkg/options/mac"
	"github.com/wailsapp/wails/v2/pkg/options/windows"
)

// 在开发模式下使用 wails dev 命令，资产从磁盘加载，任何更改都会导致“实时重新加载”。 资产的位置将从 embed.FS 推断。
//
//go:embed frontend/dist
var assets embed.FS

//go:embed build/appicon.png
var icon []byte

func main() {
	app := backend.NewApp()
	appConfig := &config.AppConfig{}
	configInfo := appConfig.GetConfig()
	update := &system.Update{}
	kafkaService := service.NewKafkaService()

	// 主应用程序由对 wails.Run() 的调用组成。 它接受描述应用程序窗口大小、窗口标题、要使用的资源等应用程序配置
	// 完整说明：https://wails.io/zh-Hans/docs/reference/options/
	err := wails.Run(&options.App{
		Title:  common.AppName,
		Width:  configInfo.Width,
		Height: configInfo.Height,
		//MinWidth:          1024,
		//MinHeight:         768,
		//MaxWidth:  1440,
		//MaxHeight: 920,
		//DisableResize:     false,
		Frameless: true, //无边框
		//HideWindowOnClose: false,  //关闭时隐藏窗口
		BackgroundColour: &options.RGBA{R: 0, G: 0, B: 0},
		AssetServer: &assetserver.Options{
			Assets: assets,
		},
		Menu: nil,
		//EnableDefaultContextMenu: false,
		//Logger:                   nil,
		//LogLevel:                 logger.DEBUG,
		//OnStartup 此回调在前端创建之后调用，但在 index.html 加载之前调用。 它提供了应用程序上下文。
		// 传递 ctx
		OnStartup: func(ctx context.Context) {
			app.Start(ctx)
			appConfig.Start(ctx)
			update.Start(ctx)
		},
		//在前端加载完毕 index.html 及其资源后调用此回调
		OnDomReady: app.DomReady,
		//在前端被销毁之后，应用程序终止之前，调用此回调。 它提供了应用程序上下文。
		OnBeforeClose: kafkaService.Close,
		//应用关闭前回调
		OnShutdown: app.Shutdown,
		//WindowStartState: options.Normal,
		//指定向前端暴露哪些结构体方法
		Bind: []any{
			app,
			appConfig,
			update,
			kafkaService,
		},
		Windows: &windows.Options{
			//WebviewIsTransparent:              false,
			//WindowIsTranslucent:               false,
			//DisableFramelessWindowDecorations: false,
			ResizeDebounceMS: 2,
		},
		Linux: &linux.Options{
			ProgramName:      common.AppName,
			Icon:             icon,
			WebviewGpuPolicy: linux.WebviewGpuPolicyOnDemand,
			//WindowIsTranslucent: false,
		},
		// Mac platform specific options
		Mac: &mac.Options{
			TitleBar: mac.TitleBarHiddenInset(),
			About: &mac.AboutInfo{
				Title:   fmt.Sprintf("%s %s", common.AppName, common.Version),
				Message: "",
				Icon:    icon,
			},
			//WebviewIsTransparent: false,
			//WindowIsTranslucent:  false,
		},
	})

	if err != nil {
		appConfig.LogErrToFile(err.Error())
		panic(err)
	}
}
