# Как опубликовать подпроект в отдельный публичный репозиторий

## Вариант 1. Через обычный Git

1. Скопируйте папку `public_analytics_training_cases` в отдельное место или создайте для нее новый репозиторий.
2. Перейдите в папку проекта:

```bash
cd projects/sber/public_analytics_training_cases
```

3. Инициализируйте Git и сделайте первый коммит:

```bash
git init
git add .
git commit -m "Initial release of analytics training cases"
```

4. Создайте пустой публичный репозиторий на GitHub.
5. Привяжите удаленный origin и отправьте код:

```bash
git remote add origin <YOUR_PUBLIC_GIT_URL>
git branch -M main
git push -u origin main
```

## Вариант 2. Через GitHub CLI

Если у вас установлен `gh`, можно сделать так:

```bash
cd projects/sber/public_analytics_training_cases
git init
git add .
git commit -m "Initial release of analytics training cases"
gh repo create analytics-training-cases --public --source=. --remote=origin --push
```

## Что проверить перед публикацией

- в `README.md` вас устраивает описание кейсов;
- в репозитории нет лишних внутренних файлов;
- Docker запускается для BI-кейса;
- notebook открывается в VS Code или Jupyter Lab;
- Excel-файл и CSV лежат в репозитории и открываются корректно.
