<p align="center">
  <img src="../../app/build/appicon.png" width="200" alt="Image">
</p>
<h1 align="center">Kafka King </h1>

<div align="center">

![License](https://img.shields.io/github/license/Bronya0/Kafka-King)
![GitHub release](https://img.shields.io/github/release/Bronya0/Kafka-King)
![GitHub All Releases](https://img.shields.io/github/downloads/Bronya0/Kafka-King/total)
![GitHub stars](https://img.shields.io/github/stars/Bronya0/Kafka-King)
![GitHub forks](https://img.shields.io/github/forks/Bronya0/Kafka-King.svg?style=flat-square)

<h3 align="center">Một GUI client Kafka hiện đại và thực dụng</h3>

</div>
<h4 align="center">
<a href="../../readme.md">English</a> | <a href="../../README-CN.md">简体中文</a> | <a href="readme-ja.md">日本語</a> | <a href="readme-ru.md">рускі</a> | <a href="readme-ko.md">한국인</a> | <a href="readme-es.md">Español</a> | <a href="readme-fr.md">Français</a> | <a href="readme-de.md">Deutsch</a> | <a href="readme-pt.md">Português</a> | <a href="readme-it.md">Italiano</a> | <a href="readme-vi.md">Tiếng Việt</a> | <a href="readme-id.md">Bahasa Indonesia</a>  
</h4>

Làm cho Kafka dễ sử dụng hơn, make kafka great again!

Dự án này là một GUI client Kafka, tương thích với nhiều hệ điều hành desktop (trừ Win7), hỗ trợ Kafka 0.8.0 đến 3.8+, được xây dựng trên Wails và franz-go. Hãy cho một ngôi sao để ủng hộ tác giả! ❤❤

> Tham khảo thêm Elasticsearch client `ES-King`, cũng rất tiện dụng: https://github.com/Bronya0/ES-King

**Doc（AI）**：[https://zread.ai/Bronya0/Kafka-King](https://zread.ai/Bronya0/Kafka-King)

# Tính năng Kafka-King
- [x] Xem danh sách node cluster, hỗ trợ cấu hình động broker và topic.
- [x] Hỗ trợ consumer client, tiêu thụ tin nhắn từ topic với group, kích thước và timeout, hiển thị chi tiết dạng bảng.
- [x] Hỗ trợ PLAIN, SSL, SASL, Kerberos, sasl_plaintext, v.v.
- [x] Hỗ trợ nén và giải nén gzip, lz4, snappy, zstd.
- [x] Tạo (hỗ trợ hàng loạt) và xóa topic, chỉ định replica và partition.
- [x] Thống kê tổng số tin nhắn, offset đã xác nhận và tồn đọng theo nhóm consumer.
- [x] Thông tin chi tiết partition (offset), hỗ trợ thêm partition mới.
- [x] Mô phỏng producer, gửi tin nhắn hàng loạt với header và partition chỉ định.
- [x] Kiểm tra sức khỏe topic và partition (hoàn tất).
- [x] Xem nhóm consumer và consumer riêng lẻ.
- [x] Báo cáo kiểm tra offset.
- [x] Hỗ trợ Schema Registry: Quản lý Subject/phiên bản, cấu hình tương thích, giải mã tin nhắn Avro, JSON, Protobuf.
- [x] Tiêu thụ luồng đa phiên (Streaming): Nhận tin nhắn thời gian thực, hiển thị đảo ngược, quản lý tab và commit offset.
- [x] Đặt lại offset nhóm tiêu thụ: Hỗ trợ đặt lại về Start (sớm nhất), End (mới nhất), timestamp hoặc offset cụ thể.
- [x] Xóa tin nhắn (DeleteRecords): Xóa tin nhắn theo phân vùng hoặc toàn bộ topic đến offset chỉ định.
- [x] Phân bổ lại bản sao phân vùng: Trực quan hóa và điều chỉnh bản sao phân vùng, hỗ trợ hủy tác vụ đang chạy.
- [x] Nâng cấp thông tin node: Đánh dấu Controller, phân tích dung lượng đĩa LogDirs, quản lý hạn ngạch (Quotas) client.
- [x] Nhập & xuất cấu hình kết nối: Xuất kết nối ra YAML, nhập từ YAML/JSON với khả năng khử trùng lặp thông minh.
- [x] Mở rộng xác thực: Hỗ trợ OAUTHBEARER (token tĩnh), AWS MSK IAM và đường hầm SSH cho nhiều broker.
- [x] Phát lại & xuất tin nhắn: Gửi lại tin nhắn đã chọn sang topic khác, xuất tin nhắn dưới dạng JSON/CSV.

# Tải xuống
Tải từ phía bên phải hoặc truy cập [trang release](https://github.com/Bronya0/Kafka-King/releases). Mở rộng 【Assets】 và chọn phiên bản phù hợp với nền tảng của bạn: Windows, macOS, Linux.

**Người dùng macOS: nếu ứng dụng báo "bị hỏng" khi mở, hãy chạy `xattr -dr com.apple.quarantine /Applications/Kafka-King.app` trong terminal (ứng dụng chưa được ký và bị Gatekeeper chặn).**

`Lưu ý quan trọng:`
1. **Trước khi sử dụng, hãy đảm bảo cấu hình `advertised.listeners` của cụm Kafka là chính xác. Nếu chưa cấu hình hoặc dùng tên miền, hãy thêm ánh xạ tên miền vào file hosts của máy bạn.**
2. **Nếu kết nối yêu cầu SSL, hãy bật TLS và bỏ qua xác thực trừ khi bạn có chứng chỉ — trong trường hợp đó hãy bật xác thực TLS và cung cấp đường dẫn chứng chỉ.**
3. **Người dùng SASL cần bật SASL, chọn giao thức SASL phù hợp (thường là plain) và nhập tên người dùng cùng mật khẩu.**
4. **Nếu gặp lỗi runtime webview2, hãy tải và cài đặt lại runtime từ trang web chính thức của Microsoft: https://developer.microsoft.com/en-us/microsoft-edge/webview2**


# Biên dịch
Chỉ cần biên dịch thủ công khi nghiên cứu mã nguồn.

cd app

wails dev

# Giấy phép
Giấy phép Apache-2.0

# Cảm ơn
- wails: https://wails.io/docs/gettingstarted/installation
- naive ui: https://www.naiveui.com/
- franz-go: https://github.com/twmb/franz-go/
- xicons: https://xicons.org/#/

# Dịch thuật
Hỗ trợ tiếng Trung, tiếng Nhật, tiếng Anh, tiếng Hàn, tiếng Nga và các ngôn ngữ khác.

Sửa hoặc thêm ngôn ngữ mới: https://github.com/Bronya0/Kafka-King/issues/51
