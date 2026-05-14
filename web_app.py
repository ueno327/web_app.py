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
    
    # 検索キーワードを取得
    search_query = request.args.get('search', '').strip()
    
    # その競技の全メンバーリスト
    all_members = GAMES[game_name]
    
    # 表示するメンバーを決定
    if search_query:
        display_members = [name for name in all_members if search_query in name]
    else:
        display_members = all_members
    
    html = """
    <div style="margin-bottom: 20px;">
        <a href="/">← 競技一覧に戻る</a>
    </div>
    
    <h1>【{{ game_name }}】出場確認</h1>

    <form action="/game/{{ game_name }}" method="get" style="margin-bottom: 30px; background: #f9f9f9; padding: 20px; border-radius: 12px; border: 2px solid #eee;">
        <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
            <input type="text" name="search" placeholder="名前を入力..." value="{{ search_query }}" 
                   style="padding: 15px; width: 350px; font-size: 1.2em; border: 1px solid #ccc; border-radius: 8px;">
            <button type="submit" 
                    style="padding: 15px 30px; font-size: 1.2em; background-color: #007bff; color: white; border: none; border-radius: 8px; cursor: pointer;">
                検索
            </button>
            {% if search_query %}
                <a href="/game/{{ game_name }}" style="margin-left: 10px; color: #666; font-size: 1.1em;">クリア</a>
            {% endif %}
        </div>
    </form>

    <p style="font-size: 1.1em; font-weight: bold; color: #333;">
        表示中: {{ display_members|length }} 名 / 全体: {{ all_members|length }} 名
    </p>

    <table border="1" style="width:100%; text-align:center; border-collapse: collapse; margin-top: 10px; font-size: 1.1em;">
        <tr style="background-color: #f2f2f2;">
            <td style="padding: 15px; {% if '(1)' in name %}color: red;{% elif '(2)' in name %}color: blue;{% elif '(3)' in name %}color: orange;{% endif %}"> {{ name }} </td>
            <th>状態</th>
            <th>操作</th>
        </tr>
        {% for name in display_members %}
        <tr style="border-bottom: 1px solid #eee;">
            <td style="padding: 15px;">{{ name }}</td>
            <td>
                {% if name in checked_in %} 
                    <span style="color: #1e7e34; font-weight: bold; font-size: 1.2em;">✅完了</span> 
                {% else %} 
                    <span style="color: #bbb;">未点呼</span> 
                {% endif %}
            </td>
            <td>
                <form action="/update" method="post" style="margin:0;">
                    <input type="hidden" name="game_name" value="{{ game_name }}">
                    <input type="hidden" name="user_name" value="{{ name }}">
                    {% if name in checked_in %}
                        <button type="submit" name="action" value="cancel" 
                                style="padding: 10px 20px; background:#d9534f; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold;">
                            取消
                        </button>
                    {% else %}
                        <button type="submit" name="action" value="checkin" 
                                style="padding: 10px 20px; background:#28a745; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold;">
                            チェックイン
                        </button>
                    {% endif %}
                </form>
            </td>
        </tr>
        {% endfor %}
    </table>

    {% if search_query and not display_members %}
        <p style="color: red; margin-top: 20px; font-size: 1.2em;">「{{ search_query }}」に一致する人は見つかりませんでした。</p>
    {% endif %}
    """
    return render_template_string(html, 
                                 game_name=game_name, 
                                 display_members=display_members, 
                                 all_members=all_members,
                                 checked_in=checked_in_data[game_name],
                                 search_query=search_query)
# --- 3. 点呼状態を更新する処理 (この部分が足りませんでした) ---
@app.post('/update')
def update_status():
    game_name = request.form.get('game_name')
    user_name = request.form.get('user_name')
    action = request.form.get('action')

    if game_name in checked_in_data:
        if action == 'checkin':
            checked_in_data[game_name].add(user_name)
        elif action == 'cancel':
            checked_in_data[game_name].discard(user_name)

    # 処理が終わったら、元の競技ページに戻る
    return redirect(url_for('game_page', game_name=game_name))