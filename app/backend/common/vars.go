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

package common

import "fmt"

var (
	// Version 会在编译时注入 -ldflags="-X 'app/backend/common.Version=${{ github.event.release.tag_name }}'"
	Version = ""
)

const (
	AppName    = "Kafka-King"
	Width      = 1180
	Height     = 760
	Theme      = "dark"
	ConfigDir  = ".kafka-king"
	ConfigPath = "config.yaml"
	ErrLogPath = "error.log"
	PingUrl    = "https://ysboke.cn/api/kingTool/ping"
)

var (
	Project          = "Bronya0/Kafka-King"
	GITHUB_URL       = fmt.Sprintf("https://github.com/%s", Project)
	GITHUB_REPOS_URL = fmt.Sprintf("https://api.github.com/repos/%s", Project)
	UPDATE_URL       = fmt.Sprintf("https://api.github.com/repos/%s/releases/latest", Project)
	ISSUES_URL       = fmt.Sprintf("https://github.com/%s/issues", Project)
	ISSUES_API_URL   = fmt.Sprintf("https://api.github.com/repos/%s/issues?state=open", Project)
)

const (
	PleaseSelectErr = "Please select a connection in the cluster"
)
