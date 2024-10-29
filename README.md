# Academic-Paper-Search-Engine
 ## How to use this dummy
1. Buat folder anda sendiri, kemudian buka vscode pada bagian terminal
2. Salin dan jalankan code berikut git clone https://github.com/arknsa/dummy_uas_nlp.git pada terminal
3. Download elasticsearch di https://www.elastic.co/downloads/elasticsearch
4. Extract elasticsearch
5. Jalankan atau buka elasticsearch\bin\elasticsearch.bat atau elasticsearch berbentuk windows batch file didalam bin
6. Kemudian di terminal python vscode, salin dan jalankan code ini venv\Scripts\activate
7. Lalu salin dan jalankan code ini pip install flask elasticsearch elasticsearch-dsl sentence-transformers
8. Lalu salin dan jalankan code ini python index_data.py
9. Lalu salin dan jalankan code ini python fetch_and_index_arxiv.py
10. Lalu salin ini http://localhost:9200/ di chrome untuk memastikan apakah elasticsearch berjalan
11. Lalu salin dan jalankan coe ini python app.py
12. Lalu salin ini http://127.0.0.1:5000 di chrome
13. Aplikasi bisa dijalankan
14. Silahkan ganti metode/model sesuai yang anda inginkan di model = SentenceTransformer('all-MiniLM-L6-v2') pada app.py
15. Jika melakukan perubahan jangan lakukan push atau pull

