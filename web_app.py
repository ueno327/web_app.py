from flask import Flask, render_template_string, request, redirect, url_for
import pandas as pd
import os

app = Flask(__name__)

# --- Excel読み込み関数 ---
def load_games_from_excel(filename):
    if not os.path.exists("data.xlsx"):
        # ファイルがない場合の初期値
        return {"データなし": []}
    
    # Excelを読み込み（A列：競技名, B列：氏名 を想定）
    df = pd.read_excel("data.xlsx")
    
    # 競技名をキー、氏名のリストを値とする辞書に変換
    # 例: {'玉入れ': ['田中太郎', '佐藤次郎'], ...}
    games_dict = df.groupby('競技名')['氏名'].apply(list).to_dict()
    return games_dict

# 1. Excelからデータを読み込む
EXCEL_FILE = 'data.xlsx'
GAMES = load_games_from_excel(EXCEL_FILE)

# チェックイン済みメンバーを保存する辞書
checked_in_data = {game: set() for game in GAMES}

# --- ページ1：競技一覧画面 ---
@app.get('/')
def index():
    # 起動中にExcelを更新した際、反映させたい場合はここで再読み込みも可能
    # GAMES = load_games_from_excel(EXCEL_FILE) 
    
    html = """
    <h1>体育祭 点呼システム</h1>
    <p>競技を選んでください（Excelから読み込み中）：</p>
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
    
    # 検索キーワードを取得（前後の空白を削除）
    search_query = request.args.get('search', '').strip()
    
    # その競技の全メンバーリスト
    all_members = GAMES[game_name]
    
    # 表示するメンバーを決定
    if search_query:
        # 検索窓に文字がある時だけ絞り込む
        display_members = [name for name in all_members if search_query in name]
    else:
        # 検索窓が空の時は全員を表示
        display_members = all_members
    
    html = """
    <div style="margin-bottom: 20px;">
        <a href="/">← 競技一覧に戻る</a>
    </div>
    
    <h1>【{{ game_name }}】出場確認</h1>

    <form action="/game/{{ game_name }}" method="get" style="margin-bottom: 20px; background: #f9f9f9; padding: 15px; border-radius: 8px; border: 1px solid #ddd;">
        <input type="text" name="search" placeholder="名前で絞り込み..." value="{{ search_query }}" style="padding: 5px; width: 200px;">
        <button type="submit" style="padding: 5px 15px;">検索</button>
        {% if search_query %}
            <a href="/game/{{ game_name }}" style="margin-left: 10px; color: #666;">クリア</a>
        {% endif %}
    </form>

    <p style="font-weight: bold;">
        表示中: {{ display_members|length }} 名 / 全体: {{ all_members|length }} 名
    </p>

    <table border="1" style="width:100%; text-align:center; border-collapse: collapse; margin-top: 10px;">
        <tr style="background-color: #f2f2f2;">
            <th style="padding: 10px;">名前</th>
            <th>状態</th>
            <th>操作</th>
        </tr>
        {% for name in display_members %}
        <tr>
            <td style="padding: 10px;">{{ name }}</td>
            <td>{% if name in checked_in %} <span style="color: green; font-weight: bold;">✅済</span> {% else %} <span style="color: #ccc;">ー</span> {% endif %}</td>
            <td>
                <form action="/update" method="post" style="margin:0;">
                    <input type="hidden" name="game_name" value="{{ game_name }}">
                    <input type="hidden" name="user_name" value="{{ name }}">
                    {% if name in checked_in %}
                        <button type="submit" name="action" value="cancel" style="background:#ffcccc; border: 1px solid #ff9999; border-radius: 3px; cursor: pointer;">取消</button>
                    {% else %}
                        <button type="submit" name="action" value="checkin" style="background:#ccffcc; border: 1px solid #99ff99; border-radius: 3px; cursor: pointer;">チェックイン</button>
                    {% endif %}
                </form>
            </td>
        </tr>
        {% endfor %}
    </table>

    {% if search_query and not display_members %}
        <p style="color: red; margin-top: 20px;">「{{ search_query }}」に一致する人は見つかりませんでした。</p>
    {% endif %}
    """
    return render_template_string(html, 
                                 game_name=game_name, 
                                 display_members=display_members,  # ここをHTML側の名前と一致させました
                                 all_members=all_members,
                                 checked_in=checked_in_data[game_name],
                                 search_query=search_query)
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