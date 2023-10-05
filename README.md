<<<<<<< HEAD
# NumericSolutions
=======
# Альфа версия приложения


## TODO чек-лист

- [ ] Добавить окно выбора исходной функции  
- [ ] Ускорить случай неявной схемы  
    - метод прогонки?  
    - scipy.linalg.solve_banded?  
    - Преобразование к трехдиагональному виду?  
- [ ] Добавить выбор реализаций схем помимо метода обратной характеристики
- [ ] Набрать реализаций для случая числа куранта > 1
    - Можно ли вывести общий алгоритм?
- [ ] верифицировать схемы  
- [ ] Подправить frontend  


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
Во все последующие разы вам необходимо будет только переключаться на созданное окружение.  
Если вам нужно просто запустить программу и не требуется собирать exe-шник, то просто войдите в консоль с питоном и пропишите последнюю команду.   


## Как это запускать?

Если все установлено правильно, то простого `python main.py` должно быть достаточно


## Как это собирать?

Для сборки exe-шника необходимо переключиться на вышеупомянутое окружение, и прописать в консоли следующее:  
`cd <путь к папке с исходниками приложения>`  
`pyinstaller --onefile -w --add-data="add.png;." .\main.py`  
после этого в папке с исходниками появится папка dist с exe-файлом  
UPD: гребаная винда стала ругаться на pyinstaller и теперь не дает собрать exe, борюсь с ней  
UPDx2: Пока придется отключать вирусную угрозу на этом файле вручную
>>>>>>> master
