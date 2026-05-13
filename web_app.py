from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# 1. ここに競技とメンバーを登録（いくらでも増やせます）
GAMES = {
    "玉入れ": ["田中太郎", "佐藤次郎", "鈴木花子", "高橋愛", "伊藤健"],
    "クラス対抗リレー": ["山本一郎", "中村美咲", "小林誠", "加藤恵"],
    "綱引き": ["田中太郎", "山本一郎", "鈴木花子", "渡辺直樹", "岡田准一"]
}

# チェックイン済みメンバーを保存する辞書 { "競技名": {名前, 名前...} }
checked_in_data = {game: set() for game in GAMES}

# --- ページ1：競技一覧画面 ---
@app.get('/')
def index():
    html = """
    <h1>体育祭 点呼システム</h1>
    <p>競技を選んでください：</p>
    <ul>
        {% for game in games_list %}
        <li>
            <a href="/game/{{ game }}" style="font-size: 1.2em; line-height: 2;">{{ game }}</a>
            ({{ checked_in[game]|length }} / {{ games_list[game]|length }} 確認済)
        </li>
        {% endfor %}
    </ul>
    """
    return render_template_string(html, games_list=GAMES, checked_in=checked_in_data)

# --- ページ2：各競技の点呼画面 ---
@app.get('/game/<game_name>')
def game_page(game_name):
    if game_name not in GAMES:
        return redirect(url_for('index'))
    
    html = """
    <a href="/">← 競技一覧に戻る</a>
    <h1>【{{ game_name }}】出場確認</h1>
    <table border="1" style="width:100%; text-align:center; border-collapse: collapse;">
        <tr style="background-color: #f2f2f2;"><th>名前</th><th>状態</th><th>操作</th></tr>
        {% for name in members %}
        <tr>
            <td>{{ name }}</td>
            <td>{% if name in checked_in %} ✅済 {% else %} ー {% endif %}</td>
            <td>
                <form action="/update" method="post" style="margin:0;">
                    <input type="hidden" name="game_name" value="{{ game_name }}">
                    <input type="hidden" name="user_name" value="{{ name }}">
                    {% if name in checked_in %}
                        <button type="submit" name="action" value="cancel" style="background:#ffcccc;">取消</button>
                    {% else %}
                        <button type="submit" name="action" value="checkin">チェックイン</button>
                    {% endif %}
                </form>
            </td>
        </tr>
        {% endfor %}
    </table>
    """
    return render_template_string(html, game_name=game_name, members=GAMES[game_name], checked_in=checked_in_data[game_name])

# --- データ更新処理 ---
@app.post('/update')
def update():
    game = request.form.get('game_name')
    name = request.form.get('user_name')
    action = request.form.get('action')
    
    if action == "checkin":
        checked_in_data[game].add(name)
    elif action == "cancel":
        checked_in_data[game].discard(name)
        
    return redirect(url_for('game_page', game_name=game))

if __name__ == "__main__":
    app.run(debug=True)