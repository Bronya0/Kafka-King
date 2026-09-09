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

<h3 align="center">Klien GUI Kafka yang modern dan praktis</h3>

</div>
<h4 align="center">
<a href="../../readme.md">English</a> | <a href="../../README-CN.md">简体中文</a> | <a href="readme-ja.md">日本語</a> | <a href="readme-ru.md">рускі</a> | <a href="readme-ko.md">한국인</a> | <a href="readme-es.md">Español</a> | <a href="readme-fr.md">Français</a> | <a href="readme-de.md">Deutsch</a> | <a href="readme-pt.md">Português</a> | <a href="readme-it.md">Italiano</a> | <a href="readme-vi.md">Tiếng Việt</a> | <a href="readme-id.md">Bahasa Indonesia</a>  
</h4>

Buat Kafka lebih mudah digunakan, make kafka great again!

Proyek ini adalah klien GUI Kafka yang kompatibel dengan berbagai sistem desktop (kecuali Win7), mendukung Kafka 0.8.0 hingga 3.8+, dibangun dengan Wails dan franz-go. Beri bintang untuk mendukung penulis! ❤❤

> Lihat juga klien Elasticsearch `ES-King`, sama praktisnya: https://github.com/Bronya0/ES-King

**Doc（AI）**：[https://zread.ai/Bronya0/Kafka-King](https://zread.ai/Bronya0/Kafka-King)

# Fitur Kafka-King
- [x] Lihat daftar node cluster, dukung konfigurasi dinamis broker dan topic.
- [x] Dukung klien konsumen, konsumsi pesan dari topic dengan grup, ukuran, dan timeout, tampilkan detail dalam tabel.
- [x] Dukung PLAIN, SSL, SASL, Kerberos, sasl_plaintext, dll.
- [x] Dukung kompresi dan dekompresi gzip, lz4, snappy, zstd.
- [x] Buat (dukung batch) dan hapus topic, tentukan replika dan partisi.
- [x] Statistik total pesan, offset yang dikonfirmasi, dan penumpukan per grup konsumen.
- [x] Informasi detail partisi (offset), dukung penambahan partisi tambahan.
- [x] Simulasi produsen, kirim pesan batch dengan header dan partisi tertentu.
- [x] Pemeriksaan kesehatan topic dan partisi (selesai).
- [x] Lihat grup konsumen dan konsumen individu.
- [x] Laporan inspeksi offset.
- [x] Dukungan Schema Registry: Manajemen Subject/versi, konfigurasi kompatibilitas, dekode pesan Avro, JSON, Protobuf.
- [x] Konsumsi streaming multi-instance: Streaming pesan real-time, urutan terbalik, manajemen tab, dan commit offset.
- [x] Reset offset grup konsumen: Reset ke Start (paling awal), End (terbaru), timestamp, atau offset tertentu.
- [x] Penghapusan pesan (DeleteRecords): Hapus pesan berdasarkan partisi atau seluruh topik hingga offset target.
- [x] Realokasi replika partisi: Inspeksi dan penyesuaian replika partisi secara visual, dengan dukungan pembatalan.
- [x] Peningkatan inspeksi node: Penanda Controller, analisis penggunaan ruang disk LogDirs, manajemen kuota client.
- [x] Impor & ekspor koneksi: Ekspor koneksi ke YAML, impor dari YAML/JSON dengan deduplikasi pintar.
- [x] Autentikasi yang diperluas: Dukungan OAUTHBEARER (token statis), AWS MSK IAM, dan SSH tunneling multi-broker.
- [x] Pemutaran ulang & ekspor pesan: Kirim ulang pesan terpilih ke topik lain, ekspor pesan ke JSON/CSV.

# Unduh
Unduh dari sisi kanan atau kunjungi [halaman rilis](https://github.com/Bronya0/Kafka-King/releases). Buka 【Assets】 dan pilih versi yang sesuai dengan platform Anda: Windows, macOS, Linux.

**Pengguna macOS: jika aplikasi menunjukkan "rusak" saat dibuka, jalankan `xattr -dr com.apple.quarantine /Applications/Kafka-King.app` di terminal (aplikasi tidak ditandatangani dan diblokir oleh Gatekeeper).**

`Catatan Penting:`
1. **Sebelum digunakan, pastikan pengaturan `advertised.listeners` cluster Kafka Anda sudah benar. Jika belum dikonfigurasi atau menggunakan nama domain, tambahkan resolusi yang sesuai di file hosts komputer Anda.**
2. **Jika koneksi Anda memerlukan SSL, aktifkan TLS dan nonaktifkan verifikasi kecuali Anda memiliki sertifikat — dalam hal ini aktifkan verifikasi TLS dan berikan jalur sertifikat.**
3. **Pengguna SASL harus mengaktifkan SASL, memilih protokol SASL yang sesuai (biasanya plain), dan memasukkan nama pengguna serta kata sandi.**
4. **Jika mengalami kesalahan runtime webview2, unduh dan instal ulang runtime dari situs resmi Microsoft: https://developer.microsoft.com/en-us/microsoft-edge/webview2**


# Membangun
Build manual hanya diperlukan untuk mempelajari kode sumber.

cd app

wails dev

# Lisensi
Lisensi Apache-2.0

# Terima Kasih
- wails: https://wails.io/docs/gettingstarted/installation
- naive ui: https://www.naiveui.com/
- franz-go: https://github.com/twmb/franz-go/
- xicons: https://xicons.org/#/

# Terjemahan
Mendukung bahasa Mandarin, Jepang, Inggris, Korea, Rusia, dan lainnya.

Perbaiki atau tambahkan bahasa baru: https://github.com/Bronya0/Kafka-King/issues/51
