"""
もぐレシピ E2Eテスト共通フィクスチャ

- .env からAPIキー・Firebase設定を読み込み
- Playwright ブラウザの起動 & index.html のファイルサーブ
- 全テストで共有するページインスタンスを提供
"""

import os
import json
import pytest
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

from dotenv import load_dotenv

# .env を読み込む (プロジェクトルート)
load_dotenv(Path(__file__).parent.parent / ".env")


# ----- ローカルHTTPサーバー -----
class QuietHandler(SimpleHTTPRequestHandler):
    """ログを出さない静かなHTTPハンドラー"""
    def log_message(self, format, *args):
        pass


_server = None
_server_thread = None
_actual_port = 0


def _start_server():
    global _server, _server_thread, _actual_port
    if _server is not None:
        return _actual_port
    root = str(Path(__file__).parent.parent)
    handler = lambda *args, **kwargs: QuietHandler(
        *args, directory=root, **kwargs
    )
    _server = HTTPServer(("127.0.0.1", 0), handler)
    _actual_port = _server.server_port
    _server_thread = threading.Thread(target=_server.serve_forever, daemon=True)
    _server_thread.start()
    return _actual_port


def _stop_server():
    global _server, _server_thread
    if _server:
        _server.shutdown()
        _server = None
        _server_thread = None


# ----- Pytest フィクスチャ -----
@pytest.fixture(scope="session")
def base_url():
    """テスト用ローカルサーバーのベースURL"""
    port = _start_server()
    yield f"http://127.0.0.1:{port}"
    _stop_server()


@pytest.fixture(scope="session")
def browser_context_args():
    """Playwright ブラウザコンテキストの設定"""
    return {
        "viewport": {"width": 390, "height": 844},  # iPhone 14 相当
        "locale": "ja-JP",
    }


@pytest.fixture(scope="session")
def env_config():
    """
    .env から読み込んだ設定を辞書で返す。
    テスト側でAPIキーやFirebase設定が必要な場合に使用。
    """
    firebase_json_str = os.getenv("FIREBASE_CONFIG", "{}")
    try:
        firebase_config = json.loads(firebase_json_str)
    except json.JSONDecodeError:
        firebase_config = {}

    return {
        "gemini_api_key": os.getenv("GEMINI_API_KEY", ""),
        "firebase_config": firebase_config,
        "firebase_config_raw": firebase_json_str,
    }


@pytest.fixture()
def page(browser, base_url):
    """
    各テストに新しいページを提供し、index.html を読み込んだ状態にする。
    テスト終了後にページを閉じる。
    """
    ctx = browser.new_context(
        viewport={"width": 390, "height": 844},
        locale="ja-JP",
    )
    pg = ctx.new_page()
    pg.goto(f"{base_url}/index.html", wait_until="networkidle")
    yield pg
    pg.evaluate("if (window.closeAllModals) window.closeAllModals()")
    pg.close()
    ctx.close()
