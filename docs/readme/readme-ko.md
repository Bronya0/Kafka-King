<p align="center">
  <img src="../../app/build/appicon.png" width="200" alt="图片标题">
</p>
<h1 align="center">Kafka King </h1>


<div align="center">

![License](https://img.shields.io/github/license/Bronya0/Kafka-King)
![GitHub release](https://img.shields.io/github/release/Bronya0/Kafka-King)
![GitHub All Releases](https://img.shields.io/github/downloads/Bronya0/Kafka-King/total)
![GitHub stars](https://img.shields.io/github/stars/Bronya0/Kafka-King)
![GitHub forks](https://img.shields.io/github/forks/Bronya0/Kafka-King.svg?style=flat-square)

<h3 align="center">현대적이고 실용적인 카프카 GUI 클라이언트 </h3>

<strong></strong>
</div>
<h4 align="center">
<a href="../../readme.md">English</a> | <a href="../../README-CN.md">简体中文</a> | <a href="readme-ja.md">日本語</a> | <a href="readme-ru.md">рускі</a> | <a href="readme-ko.md">한국인</a> | <a href="readme-es.md">Español</a> | <a href="readme-fr.md">Français</a> | <a href="readme-de.md">Deutsch</a> | <a href="readme-pt.md">Português</a> | <a href="readme-it.md">Italiano</a> | <a href="readme-vi.md">Tiếng Việt</a> | <a href="readme-id.md">Bahasa Indonesia</a>  
</h4>

카프카를 더욱 편리하게 사용하세요, make kafka great again!

이 프로젝트는 각종 시스템을 지원하는 카프카 GUI 클라이언트입니다. 작성자님의 열심히 공개한 소스를 지원해주시려면 스타를 눌러주세요. 감사합니다❤❤

> 유사하게 편리한 엘라스틱서치 클라이언트 `ES-King`도 함께 저장해두시면 좋습니다: https://github.com/Bronya0/ES-King





# Kafka-King 기능 목록
- [x] 클러스터 노드 목록 보기, 브로커, 토픽 구성 항목의 동적 구성 지원
- [x] 소비자 클라이언트 지원, 지정된 그룹에 따라 지정된 토픽, 크기, 타임아웃으로 소비하며, 메시지의 각 차원 정보를 표 형태로 보여줍니다.
- [x] PLAIN, SSL, SASL, kerberos, sasl_plaintext 등을 지원합니다.
- [x] 메시지 gzip, lz4, snappy, zstd 압축 및 압축 해제 지원
- [x] 토픽 생성(대량 지원), 토픽 삭제, 복제본, 파티션 지정
- [x] 소비자 그룹에 따라 각 토픽의 메시지 총량, 제출 총량, 백로그량을 통계할 수 있습니다.
- [x] 토픽의 파티션 세부 정보(오프셋)를 보고, 추가 파티션을 추가할 수 있습니다.
- [x] 프로듀서를 모사하여 메시지를 대량으로 전송하고, 헤더, 파티션을 지정할 수 있습니다.
- [x] 토픽, 파티션 건강 검사(완료)
- [x] 소비자 그룹, 소비자를 보기 지원
- [x] 오프셋 순찰 보고서
- [x] Schema Registry 지원: Subject/버전 관리, 호환성 설정, Avro/JSON/Protobuf 메시지 디코딩
- [x] 다중 스트리밍 컨슘: 다중 스트림 실시간 메시지 수신, 역순 보기, 탭 관리 및 오프셋 커밋
- [x] 컨슈머 그룹 오프셋 재설정: 가장 이른(Start), 최신(End), 타임스탬프, 지정 오프셋 재설정 지원
- [x] 메시지 정리 (DeleteRecords): 지정 파티션 또는 전체 파티션 메시지 삭제 및 전체 비우기 지원
- [x] 파티션 복제본 재할당: 복제본 분배 시각화 및 조정, 진행 중인 재할당 취소 지원
- [x] 노드 정보 강화: Controller 노드 표시, LogDirs 디스크 사용량 분석, 클라이언트 Quotas(할당량) 관리
- [x] 연결 설정 가져오기 및 내보내기: 전체 연결 설정을 YAML/JSON으로 내보내기 및 중복 제거 가져오기 지원
- [x] 인증 지원 확장: OAUTHBEARER(정적 토큰), AWS MSK IAM 및 멀티 브로커 SSH 터널링 지원
- [x] 메시지 재생 및 내보내기: 선택한 메시지를 다른 토픽으로 재전송 및 JSON/CSV 내보내기 지원

# 다운로드
오른쪽에서 다운로드하거나 [다운로드 주소](https://github.com/Bronya0/Kafka-King/releases)를 클릭하여 【Assets】를 펼치고 자신의 플랫폼에 맞게 다운로드하세요. Windows, macOS, Linux를 지원합니다.

**macOS 사용자: 앱이 "손상됨"으로 표시되며 열리지 않는 경우, 터미널에서 `xattr -dr com.apple.quarantine /Applications/Kafka-King.app`을 실행하세요 (앱이 서명되지 않아 Gatekeeper에 의해 차단되었기 때문입니다).**

`반드시 읽어야 할 주의 사항:`

> 1. **사용 전에 카프카 클러스터 구성의 `advertised.listeners`를 확인하세요. 구성되어 있지 않거나 도메인 이름으로 구성되어 있다면 King에서 연결 주소를 입력할 때, 해당 도메인 이름을 로컬 컴퓨터의 hosts 파일에 미리 추가해야 합니다. 그렇지 않으면 도메인 이름을 해석할 수 없기 때문에 연결할 수 없으며, King 입력란에 IP를 입력하더라도 마찬가지입니다.**
>
> 2. **연결에 SSL이 필요한 경우 TLS를 체크하고 인증 무시를 체크하세요(인증서가 있다면 다운로드하여 tls 인증을 활성화하고 인증서 경로를 입력하세요).**
>
> 3. **SASL 메커니즘 사용자는 SASL을 활성화하고 SASL 프로토콜(보통은 plain)을 선택하고, 사용자 이름과 비밀번호를 입력해야 합니다.**
>
> 4. **WebView2 런타임 오류가 발생하면 Microsoft 웹사이트에서 런타임을 다시 다운로드하여 설치하세요: https://developer.microsoft.com/zh-cn/microsoft-edge/webview2**



# 빌드
원시 코드를 연구해야만 수동으로 빌드가 필요합니다.

cd app

wails dev


# 라이선스
Apache-2.0 라이선스

# 감사합니다
- wails：https://wails.io/docs/gettingstarted/installation
- naive ui：https://www.naiveui.com/
- franz-go：https://github.com/twmb/franz-go/
- xicons：https://xicons.org/#/

# TransLate
중국어, 일본어, 영어, 한국어, 러시아어 및 기타 언어 지원

새로운 언어 수정 또는 추가：https://github.com/Bronya0/Kafka-King/issues/51
