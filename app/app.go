package main

import (
	"app/backend/common"
	"context"
	"crypto/tls"
	"github.com/go-resty/resty/v2"
	"runtime"
)

// App struct
type App struct {
	ctx context.Context
}

// NewApp creates a new App application struct
func NewApp() *App {
	return &App{}
}

// Start is called at application startup
func (a *App) Start(ctx context.Context) {
	// Perform your setup here
	a.ctx = ctx
}

// domReady is called after front-end resources have been loaded
func (a *App) domReady(ctx context.Context) {

	// 统计版本使用情况
	client := resty.New().SetTLSClientConfig(&tls.Config{InsecureSkipVerify: true})
	body := map[string]interface{}{
		"name":     "Kafka-King",
		"version":  common.Version,
		"platform": runtime.GOOS,
	}
	_, _ = client.R().SetBody(body).Post(common.PingUrl)

}

// beforeClose is called when the application is about to quit,
// either by clicking the window close button or calling runtime.Quit.
// Returning true will cause the application to continue, false will continue shutdown as normal.
func (a *App) beforeClose(ctx context.Context) (prevent bool) {
	return false
}

// shutdown is called at application termination
func (a *App) shutdown(ctx context.Context) {
	// Perform your teardown here
}
