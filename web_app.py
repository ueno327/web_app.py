from flask import Flask, render_template_string, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'secret_key_for_session' # 確認メッセージ（flash）を使うために必要

# --- 名簿データ（本来はデータベースを使いますが、今回は簡易的にリストで） ---
members = ["田中 太郎", "佐藤 花子", "鈴木 一郎", "高橋 健二"]
checked_in_list = []

# HTMLのデザイン（1つのファイルで完結させるために文字列で定義します）
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>チェックインアプリ</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; text-align: center; padding: 20px; background: #f0f2f5; }
        .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); max-width: 400px; margin: auto; }
        button { background: #007AFF; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-size: 16px; }
        select { width: 100%; padding: 10px; margin-bottom: 20px; font-size: 16px; }
    </style>
    <script>
        function confirmCheckIn() {
            // 1回目の確認
            if (confirm("チェックインしますか？")) {
                // 2回目の確認
                return confirm("【最終確認】本当によろしいですか？");
            }
            return false;
        }
    </script>
</head>
<body>
    <div class="card">
        <h2>チェックイン名簿</h2>
        <form method="POST" onsubmit="return confirmCheckIn()">
            <select name="user_name" required size="5">
                {% for name in members %}
                    <option value="{{ name }}">{{ name }}</option>
                {% endfor %}
            </select>
            <br>
            <button type="submit">チェックインする</button>
        </form>

        {% with messages = get_flashed_messages() %}
          {% if messages %}
            {% for message in messages %}
              <p style="color: green; font-weight: bold; margin-top: 20px;">{{ message }}</p>
            {% endfor %}
          {% endif %}
        {% endwith %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('user_name')
        if name in members:
            members.remove(name) # 名簿から消す
            checked_in_list.append(name) # チェックイン済みへ
            flash(f"{name}さんのチェックインが完了しました！")
        return redirect(url_for('index'))
    
    return render_template_string(HTML_TEMPLATE, members=members)

if __name__ == '__main__':
    app.run(debug=True, port=5000)