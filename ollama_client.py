# save_as: ollama_client.py
import requests
import json
import time

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
        self.session = requests.Session()
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def check_health(self):
        try:
            response = self.session.get(f"{self.base_url}/", timeout=10)
            return response.status_code == 200
        except requests.exceptions.ConnectionError:
            print("❌ Сервер недоступен. Проверьте что Ollama запущен:")
            print("docker-compose ps")
            return False

    def generate_text(self, model, prompt, max_retries=3):
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 200
            }
        }

        for attempt in range(max_retries):
            try:
                response = self.session.post(
                    f"{self.base_url}/api/generate",
                    headers=self.headers,
                    data=json.dumps(payload),
                    timeout=1000  # максимальное время ожидания в секундах
                )
                
                if response.status_code == 200:
                    return response.json().get('response')
                else:
                    print(f"⚠️ Ошибка API (код {response.status_code}): {response.text}")
                    time.sleep(2 ** attempt)  # Экспоненциальная задержка
                    
            except requests.exceptions.RequestException as e:
                print(f"🚨 Сетевая ошибка: {str(e)}")
                time.sleep(5)

        return None

if __name__ == "__main__":
    client = OllamaClient()
    
    if not client.check_health():
        exit(1)
    
    # Тестовый запрос
    response = client.generate_text(
        model="deepseek-coder:6.7b",
        prompt='Напиши от первого лица на русском языке релевантный комментарий к посту у которого текст:"Василий успешно развернул DeepSeek локально в docker-compose"'
    )
    
    if response:
        print("✅ Ответ модели:")
        print(response)
    else:
        print("❌ Не удалось получить ответ. Проверьте:")
        print("1. Загружена ли модель: docker-compose exec ollama ollama list")
        print("2. Достаточно ли памяти: free -h")