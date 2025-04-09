#!/bin/bash

# Скрипт автоматизации деплоя проекта ELAI на GitHub

# Устанавливаем переменные
REPO_URL="https://github.com/DmitriyTchk/elai.git"
BRANCH="main"

echo "🔧 Подготовка репозитория..."

# Переход в корневую папку проекта
cd "$(dirname "$0")"

# Добавление всех файлов
git add .

# Коммит изменений
git commit -m "Deploy ELAI project"

# Создание главной ветки, если еще не создана
git branch -M $BRANCH

# Добавление удаленного репозитория (если еще не добавлен)
git remote add origin $REPO_URL 2>/dev/null

# Пуш изменений в GitHub
git push -u origin $BRANCH

echo "✅ Проект успешно загружен на GitHub!"
