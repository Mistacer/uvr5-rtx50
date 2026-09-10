# -*- coding: utf-8 -*-
"""UVR5 界面语言支持（i18n）。

- 语言文件放在 gui_data/lang/<code>.json，格式为 {"英文原文": "译文"}。
- 默认语言：先读 gui_data/ui_lang.txt（安装程序按系统显示语言写入），
  读不到再看系统 locale，最后回退英文。
- 翻译只改控件的显示文字，不修改任何内部逻辑值（下拉框的 values 不动），
  因此不会影响模型名、方法名等用于比较 / 存盘的字符串。
"""

import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_LANG_DIR = os.path.join(_HERE, 'lang')
_PREF_FILE = os.path.join(_HERE, 'ui_lang.txt')

LANGUAGES = (
    ('en', 'English'),
    ('zh_CN', '简体中文'),
)

_catalog = {}
_current = 'en'
_hooked = False


def available():
    """返回 [(code, 显示名), ...]"""
    return list(LANGUAGES)


def display_names():
    return [name for _code, name in LANGUAGES]


def display_name(code):
    for c, name in LANGUAGES:
        if c == code:
            return name
    return LANGUAGES[0][1]


def code_from_display(name):
    for c, n in LANGUAGES:
        if n == name:
            return c
    return None


def get_language():
    return _current


def _catalog_path(code):
    return os.path.join(_LANG_DIR, code + '.json')


def load(code):
    """载入语言词典。找不到对应文件时回退英文。"""
    global _catalog, _current
    code = (code or 'en').strip()
    if not code_from_display(display_name(code)) or code not in [c for c, _ in LANGUAGES]:
        code = 'en'
    _catalog = {}
    if code == 'en':
        _current = 'en'
        return
    path = _catalog_path(code)
    if os.path.isfile(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict):
                _catalog = {k: v for k, v in data.items() if isinstance(k, str) and isinstance(v, str)}
                _current = code
                return
        except Exception:
            pass
    _current = 'en'


def detect_default():
    """安装时写入的偏好 > 系统语言 > 英文。"""
    try:
        with open(_PREF_FILE, 'r', encoding='utf-8') as f:
            code = f.read().strip()
        if code in [c for c, _ in LANGUAGES]:
            return code
    except Exception:
        pass
    try:
        import locale
        loc = ''
        try:
            loc = locale.getlocale()[0] or ''
        except Exception:
            loc = ''
        if not loc:
            try:
                loc = locale.getdefaultlocale()[0] or ''
            except Exception:
                loc = ''
        if loc.lower().replace('-', '_').startswith('zh'):
            return 'zh_CN'
    except Exception:
        pass
    return 'en'


def set_language_preference(code):
    """保存语言偏好（下次启动生效）。"""
    try:
        with open(_PREF_FILE, 'w', encoding='utf-8') as f:
            f.write(code)
        return True
    except Exception:
        return False


def tr(text):
    """翻译一条字符串；没有译文就原样返回。"""
    if not text or _current == 'en':
        return text
    return _catalog.get(text, text)


# ----------------------------------------------------------------------
#  tkinter 钩子：在控件创建 / 改文字时自动翻译
# ----------------------------------------------------------------------

def _translate_dict(d):
    """把 dict 里的 text / title 换成译文，返回（可能是新的）dict。"""
    if not isinstance(d, dict):
        return d
    out = d
    for key in ('text', 'title'):
        v = out.get(key)
        if isinstance(v, str):
            t = tr(v)
            if t != v:
                if out is d:
                    out = dict(d)
                out[key] = t
    return out


def install_hooks():
    global _hooked
    if _hooked:
        return
    _hooked = True

    import tkinter as tk
    from tkinter import ttk

    # ---- tk 控件 ----
    _base_init = tk.BaseWidget.__init__

    def base_init(self, master, widgetName, cnf={}, kw={}, extra=()):
        cnf = _translate_dict(cnf)
        kw = _translate_dict(kw)
        _base_init(self, master, widgetName, cnf, kw, extra)

    tk.BaseWidget.__init__ = base_init

    _misc_configure = tk.Misc.configure

    def misc_configure(self, cnf=None, **kw):
        cnf = _translate_dict(cnf)
        kw = _translate_dict(kw)
        return _misc_configure(self, cnf, **kw)

    tk.Misc.configure = misc_configure

    _misc_setitem = tk.Misc.__setitem__

    def misc_setitem(self, key, value):
        if key == 'text' and isinstance(value, str):
            value = tr(value)
        return _misc_setitem(self, key, value)

    tk.Misc.__setitem__ = misc_setitem

    # ---- ttk 控件 ----
    _ttk_init = ttk.Widget.__init__

    def ttk_init(self, master, widgetName, kw=None):
        kw = _translate_dict(kw)
        _ttk_init(self, master, widgetName, kw)

    ttk.Widget.__init__ = ttk_init

    _ttk_configure = ttk.Widget.configure

    def ttk_configure(self, cnf=None, **kw):
        cnf = _translate_dict(cnf)
        kw = _translate_dict(kw)
        return _ttk_configure(self, cnf, **kw)

    ttk.Widget.configure = ttk_configure

    # ---- Notebook 标签页 ----
    _nb_add = ttk.Notebook.add

    def nb_add(self, child, **kw):
        kw = _translate_dict(kw)
        return _nb_add(self, child, **kw)

    ttk.Notebook.add = nb_add

    _nb_tab = ttk.Notebook.tab

    def nb_tab(self, tab_id, option=None, **kw):
        kw = _translate_dict(kw)
        return _nb_tab(self, tab_id, option, **kw)

    ttk.Notebook.tab = nb_tab

    # ---- 菜单 ----
    for _name in ('add_command', 'add_cascade', 'add_checkbutton', 'add_radiobutton'):
        _orig = getattr(tk.Menu, _name)

        def _wrap(orig):
            def inner(self, cnf={}, **kw):
                if isinstance(cnf, dict) and isinstance(cnf.get('label'), str):
                    cnf['label'] = tr(cnf['label'])
                if isinstance(kw.get('label'), str):
                    kw['label'] = tr(kw['label'])
                return orig(self, cnf, **kw)
            return inner

        setattr(tk.Menu, _name, _wrap(_orig))

    # ---- 窗口标题 ----
    _wm_title = tk.Wm.title

    def wm_title(self, string=None):
        if isinstance(string, str):
            string = tr(string)
        return _wm_title(self, string)

    tk.Wm.title = wm_title

    # ---- 对话框 ----
    try:
        from tkinter import messagebox as _mb
        for _name in ('showinfo', 'showwarning', 'showerror', 'askyesno', 'askokcancel',
                      'askquestion', 'askyesnocancel', 'askretrycancel'):
            _orig = getattr(_mb, _name, None)
            if _orig is None:
                continue

            def _wrap_mb(orig):
                def inner(title=None, message=None, **options):
                    if isinstance(title, str):
                        title = tr(title)
                    if isinstance(message, str):
                        message = tr(message)
                    return orig(title, message, **options)
                return inner

            setattr(_mb, _name, _wrap_mb(_orig))
    except Exception:
        pass

    try:
        from tkinter import filedialog as _fd
        for _name in ('askopenfilename', 'askopenfilenames', 'asksaveasfilename', 'askdirectory'):
            _orig = getattr(_fd, _name, None)
            if _orig is None:
                continue

            def _wrap_fd(orig):
                def inner(**options):
                    if isinstance(options.get('title'), str):
                        options['title'] = tr(options['title'])
                    return orig(**options)
                return inner

            setattr(_fd, _name, _wrap_fd(_orig))
    except Exception:
        pass

    try:
        from tkinter import simpledialog as _sd
        _orig_ask = _sd.askstring

        def askstring(title, prompt, **kw):
            if isinstance(title, str):
                title = tr(title)
            if isinstance(prompt, str):
                prompt = tr(prompt)
            return _orig_ask(title, prompt, **kw)

        _sd.askstring = askstring
    except Exception:
        pass


def init():
    """启动时调用：载入语言并安装钩子。"""
    load(detect_default())
    install_hooks()
    return _current
