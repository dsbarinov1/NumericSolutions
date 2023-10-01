# Альфа версия приложения


## Как это устанавливать?

Во-первых, в анаконде необходимо создать под этот проект отдельное окружение(иначе потом при сборке exe-шника он будет весить под 300мб вместе со всеми вашими ненужными библиотеками)
Для этого заходим в *Anaconda Promt* (если у вас установлена анасонда) и пишем:  
`conda create --name <ваше название окружения> python=3.9`  
После этого конда предложит его создать, выбираем *yes* и проверяем его наличие:  
`conda env list`  
Ваше название должно появиться в списке. Далее переключаемся на него с помощью  
`conda activate <ваше название окружения>`  
И устанавливаем необходимые пакеты с помощью файла из этого репозитория:  
`pip install -r <путь к скачанному req.txt>`  
Во все последующие разы вам необходимо будет только переключаться на созданное окружение  


## Как это запускать?

Если все установлено правильно, то простого `python main.py` должно быть достаточно


## Как это собирать?

Для сборки exe-шника необходимо переключиться на вышеупомянутое окружение, и прописать в консоли следующее:  
`cd <путь к папке с исходниками приложения>`  
`pyinstaller --onefile -w --add-data="add.png;." .\main.py`  
после этого в папке с исходниками появится папка dist с exe-файлом  
UPD: гребаная винда стала ругаться на pyinstaller и теперь не дает собрать exe, бьюсь с ней  
UPDx2: Пока придется отключать вирусную угрозу на этом файле вручную
