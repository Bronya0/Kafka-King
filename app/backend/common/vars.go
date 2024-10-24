package common

import "fmt"

var (
	// Version 会在编译时注入 -ldflags="-X 'app/backend/common.Version=${{ github.event.release.tag_name }}'"
	Version = ""
)

const (
	AppName    = "Kafka-King"
	Width      = 1600
	Height     = 870
	Theme      = "dark"
	ConfigDir  = ".kafka-king"
	ConfigPath = "config.yaml"
	Language   = "zh-CN"
	PingUrl    = "https://ysboke.cn/api/kingTool/ping"
)

var (
	Project          = "Bronya0/ES-King"
	GITHUB_URL       = fmt.Sprintf("https://github.com/%s", Project)
	GITHUB_REPOS_URL = fmt.Sprintf("https://api.github.com/repos/%s", Project)
	UPDATE_URL       = fmt.Sprintf("https://api.github.com/repos/%s/releases/latest", Project)
	ISSUES_URL       = fmt.Sprintf("https://github.com/%s/issues", Project)
	ISSUES_API_URL   = fmt.Sprintf("https://api.github.com/repos/%s/issues?state=open", Project)
)
