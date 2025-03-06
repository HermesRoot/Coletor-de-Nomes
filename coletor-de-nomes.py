import os
import threading
import json
import wx
import gettext
import io

def setup_language(lang="pt_BR"):
    # Caminho ajustado para apontar diretamente para locale/<lang>/<lang>.mo
    localedir = os.path.join(os.path.dirname(__file__), "locale", lang)
    mo_file = os.path.join(localedir, f"{lang}.mo")
    print(f"Tentando carregar tradução para {lang} em {mo_file}")
    
    try:
        # Carrega o arquivo .mo diretamente
        with open(mo_file, 'rb') as f:
            translation = gettext.GNUTranslations(f)
        translation.install()
        print(f"Tradução para {lang} carregada com sucesso")
        test_str = translation.gettext("File Name Collector")
        print(f"Teste de tradução: 'File Name Collector' -> '{test_str}'")
        return translation.gettext
    except FileNotFoundError:
        print(f"Arquivo de tradução {mo_file} não encontrado. Usando texto padrão.")
        return lambda s: s
    except Exception as e:
        print(f"Erro ao carregar tradução: {e}")
        return lambda s: s

# Inicializa a tradução
_ = setup_language("pt_BR")

class FileCollectorFrame(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(500, 400))
        self.last_saved_path = None
        self.default_save_dir = ""
        self.config_file = os.path.join(os.path.dirname(__file__), "config.json")
        self.current_lang = "pt_BR"
        self.load_config()
        self.init_ui()

    def create_menu(self):
        menubar = wx.MenuBar()
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_NEW, _('New Scan'))
        file_menu.Append(wx.ID_SAVEAS, _('Save As...'))
        file_menu.AppendSeparator()
        file_menu.Append(wx.ID_ANY, _('View Current Log'))
        file_menu.AppendSeparator()
        file_menu.Append(wx.ID_EXIT, _('Exit'))
        menubar.Append(file_menu, _('File'))

        config_menu = wx.Menu()
        self.config_ext_id = config_menu.Append(wx.ID_ANY, _('Set Default Extensions...')).GetId()
        self.config_dir_id = config_menu.Append(wx.ID_ANY, _('Set Default Save Location...')).GetId()

        lang_menu = wx.Menu()
        self.portugues_item = lang_menu.Append(wx.ID_ANY, "Português", kind=wx.ITEM_RADIO)
        self.ingles_item = lang_menu.Append(wx.ID_ANY, "English", kind=wx.ITEM_RADIO)
        self.portugues_item.Check(self.current_lang == "pt_BR")
        self.ingles_item.Check(self.current_lang == "en_US")
        config_menu.AppendSubMenu(lang_menu, _("Language"))

        menubar.Append(config_menu, _('Settings'))

        help_menu = wx.Menu()
        self.how_to_id = help_menu.Append(wx.ID_ANY, _('How to Use')).GetId()
        help_menu.Append(wx.ID_ABOUT, _('About...'))
        menubar.Append(help_menu, _('Help'))

        self.Bind(wx.EVT_MENU, self.on_new_scan, id=wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self.on_save_as, id=wx.ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self.on_view_log, id=file_menu.FindItem(_('View Current Log')))
        self.Bind(wx.EVT_MENU, self.on_exit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.on_about, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.on_set_default_extensions, id=self.config_ext_id)
        self.Bind(wx.EVT_MENU, self.on_set_default_save_dir, id=self.config_dir_id)
        self.Bind(wx.EVT_MENU, self.on_how_to_use, id=self.how_to_id)
        self.Bind(wx.EVT_MENU, self.on_change_lang, self.portugues_item)
        self.Bind(wx.EVT_MENU, self.on_change_lang, self.ingles_item)

        return menubar

    def init_ui(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.extension_label = wx.StaticText(panel, label=_("Filter Extensions (comma-separated, e.g., .txt,.jpg)"))
        vbox.Add(self.extension_label, flag=wx.LEFT | wx.TOP, border=10)

        self.extension_text = wx.TextCtrl(panel, value=self.default_extensions)
        self.extension_text.SetToolTip(_("Separate extensions with commas, e.g., .txt, .jpg"))
        vbox.Add(self.extension_text, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)

        self.recursive_checkbox = wx.CheckBox(panel, label=_("Include Subfolders"))
        self.recursive_checkbox.SetToolTip(_("Includes files from all subfolders of the selected folder"))
        vbox.Add(self.recursive_checkbox, flag=wx.LEFT | wx.TOP, border=10)

        self.include_folders_checkbox = wx.CheckBox(panel, label=_("Include Folder Names"))
        self.include_folders_checkbox.SetToolTip(_("Adds folder names to the output file"))
        vbox.Add(self.include_folders_checkbox, flag=wx.LEFT | wx.TOP, border=10)

        self.folder_label = wx.StaticText(panel, label=_("Selected Folder: None"))
        vbox.Add(self.folder_label, flag=wx.LEFT | wx.TOP, border=10)

        self.scan_button = wx.Button(panel, label=_("Scan Folder"))
        self.scan_button.Bind(wx.EVT_BUTTON, self.on_scan)
        vbox.Add(self.scan_button, flag=wx.ALL | wx.ALIGN_CENTER, border=10)

        self.result_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        vbox.Add(self.result_text, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        panel.SetSizer(vbox)

        menubar = self.create_menu()
        self.SetMenuBar(menubar)
        self.Centre()
        self.Show()

    def load_config(self):
        default_config = {"extensions": "", "last_path": "", "default_save_dir": "", "language": "pt_BR"}
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                print(f"Config carregado: {config}")
        except FileNotFoundError:
            config = default_config
            print("Arquivo config.json não encontrado. Usando configuração padrão.")
        except PermissionError:
            config = default_config
            wx.MessageBox(_("Permission denied to read config file. Using defaults."), _("Warning"), wx.OK | wx.ICON_WARNING)
        self.default_extensions = config.get("extensions", "")
        self.last_saved_path = config.get("last_path", "")
        self.default_save_dir = config.get("default_save_dir", "")
        self.current_lang = config.get("language", "pt_BR")
        print(f"Idioma atual definido como: {self.current_lang}")

    def save_config(self):
        config = {
            "extensions": self.extension_text.GetValue(),
            "last_path": self.last_saved_path or "",
            "default_save_dir": self.default_save_dir,
            "language": self.current_lang
        }
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f)
                print(f"Config salvo: {config}")
        except PermissionError:
            wx.MessageBox(_("Permission denied to save config file: {}").format(self.config_file), 
                          _("Error"), wx.OK | wx.ICON_ERROR)
        except Exception as e:
            wx.MessageBox(_("Error saving settings: {}").format(str(e)), _("Error"), wx.OK | wx.ICON_ERROR)

    def on_new_scan(self, event):
        self.extension_text.SetValue(self.default_extensions)
        self.recursive_checkbox.SetValue(False)
        self.include_folders_checkbox.SetValue(False)
        self.folder_label.SetLabel(_("Selected Folder: None"))
        self.result_text.Clear()

    def on_save_as(self, event):
        if self.last_saved_path and os.path.exists(self.last_saved_path):
            with wx.FileDialog(self, _("Save file list as"), wildcard="Text files (*.txt)|*.txt",
                               style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
                               defaultDir=self.default_save_dir or os.getcwd()) as save_dlg:
                if save_dlg.ShowModal() == wx.ID_OK:
                    save_path = save_dlg.GetPath()
                    try:
                        with open(self.last_saved_path, 'r', encoding='utf-8') as original, \
                             open(save_path, 'w', encoding='utf-8') as copy:
                            copy.write(original.read())
                        wx.MessageBox(_("Saved to {}").format(save_path), _("Completed"), wx.OK | wx.ICON_INFORMATION)
                    except Exception as e:
                        wx.MessageBox(_("Error saving: {}").format(str(e)), _("Error"), wx.OK | wx.ICON_ERROR)

    def on_view_log(self, event):
        if self.last_saved_path and os.path.exists(self.last_saved_path):
            try:
                os.startfile(self.last_saved_path)
            except Exception as e:
                wx.MessageBox(_("Error opening file: {}").format(str(e)), _("Error"), wx.OK | wx.ICON_ERROR)

    def on_exit(self, event):
        self.save_config()
        self.Close()

    def on_about(self, event):
        wx.MessageBox(_("File Name Collector\nby HermesRoot\nVersion: 0.1.0"), 
                      _("About"), wx.OK | wx.ICON_INFORMATION)

    def on_set_default_extensions(self, event):
        dlg = wx.TextEntryDialog(self, _("Enter default extensions (e.g., .txt,.jpg):"), 
                                 _("Set Default Extensions"), self.default_extensions)
        if dlg.ShowModal() == wx.ID_OK:
            self.default_extensions = dlg.GetValue()
            self.extension_text.SetValue(self.default_extensions)
            self.save_config()
        dlg.Destroy()

    def on_set_default_save_dir(self, event):
        with wx.DirDialog(self, _("Select default save directory"), 
                          defaultPath=self.default_save_dir or os.getcwd()) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self.default_save_dir = dlg.GetPath()
                self.save_config()

    def on_how_to_use(self, event):
        instructions = (
            _("How to Use File Name Collector:\n\n"
              "1. Click 'Scan Folder' to choose a folder.\n"
              "2. Optional: Enter extensions (e.g., .txt,.jpg) to filter files.\n"
              "3. Check 'Include Subfolders' to scan subdirectories.\n"
              "4. Check 'Include Folder Names' to list folders.\n"
              "5. Choose where to save the output file.\n"
              "6. View results in the window or generated file.\n\n"
              "Use 'Settings' to set defaults and 'Save As...' to create copies of the result.")
        )
        wx.MessageBox(instructions, _("How to Use"), wx.OK | wx.ICON_INFORMATION)

    def on_change_lang(self, event):
        lang_map = {"Português": "pt_BR", "English": "en_US"}
        menu_item = self.GetMenuBar().FindItemById(event.GetId())
        new_lang = lang_map[menu_item.GetItemLabelText()]
        if new_lang != self.current_lang:
            self.current_lang = new_lang
            global _
            _ = setup_language(new_lang)  # Usa a função ajustada
            self.save_config()
            self.refresh_ui()

    def refresh_ui(self):
        print(f"Atualizando UI para idioma: {self.current_lang}")
        self.extension_label.SetLabel(_("Filter Extensions (comma-separated, e.g., .txt,.jpg)"))
        self.recursive_checkbox.SetLabel(_("Include Subfolders"))
        self.include_folders_checkbox.SetLabel(_("Include Folder Names"))
        self.folder_label.SetLabel(_("Selected Folder: None"))
        self.scan_button.SetLabel(_("Scan Folder"))
        self.SetTitle(_("File Name Collector"))
        self.SetMenuBar(None)
        menubar = self.create_menu()
        self.SetMenuBar(menubar)
        self.Layout()
        self.Centre()

    def on_scan(self, event):
        with wx.DirDialog(self, _("Select a folder")) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                folder_path = dlg.GetPath()
                self.folder_label.SetLabel(_("Selected Folder: {}").format(folder_path))
                extensions_raw = self.extension_text.GetValue()
                extensions = self.validate_extensions(extensions_raw)
                if extensions is None:
                    return

                include_subfolders = self.recursive_checkbox.GetValue()
                include_folders = self.include_folders_checkbox.GetValue()

                with wx.FileDialog(self, _("Save file list"), 
                                   defaultDir=self.default_save_dir or os.getcwd(),
                                   wildcard="Text files (*.txt)|*.txt", 
                                   style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
                                   defaultFile=f"{os.path.basename(folder_path)}_file_list.txt") as save_dlg:
                    if save_dlg.ShowModal() == wx.ID_OK:
                        save_path = save_dlg.GetPath()
                        self.last_saved_path = save_path
                        threading.Thread(target=self.collect_and_write, 
                                         args=(folder_path, extensions, include_subfolders, include_folders, save_path), 
                                         daemon=True).start()

    def validate_extensions(self, extensions_raw):
        extensions = [ext.strip() for ext in extensions_raw.split(',') if ext.strip()]
        invalid_extensions = [ext for ext in extensions if not ext.startswith('.')]
        if invalid_extensions:
            wx.MessageBox(_("Invalid extensions: {}. All must start with '.'").format(', '.join(invalid_extensions)),
                          _("Error"), wx.OK | wx.ICON_ERROR)
            return None
        return extensions

    def collect_files_generator(self, folder_path, extensions, include_subfolders, include_folders):
        try:
            if include_subfolders:
                for root, dirs, files in os.walk(folder_path):
                    if include_folders:
                        yield os.path.basename(root), True
                    for file in files:
                        if not extensions or any(file.endswith(ext) for ext in extensions):
                            yield file, False
            else:
                for item in os.listdir(folder_path):
                    full_path = os.path.join(folder_path, item)
                    if os.path.isdir(full_path) and include_folders:
                        yield item, True
                    elif os.path.isfile(full_path) and (not extensions or any(item.endswith(ext) for ext in extensions)):
                        yield item, False
        except PermissionError:
            wx.CallAfter(wx.MessageBox, _("Permission denied accessing folder."), _("Error"), wx.OK | wx.ICON_ERROR)
            raise
        except Exception as e:
            wx.CallAfter(wx.MessageBox, _("Error scanning: {}").format(str(e)), _("Error"), wx.OK | wx.ICON_ERROR)
            raise

    def collect_and_write(self, folder_path, extensions, include_subfolders, include_folders, save_path):
        file_names = []
        folder_names = []

        try:
            generator = self.collect_files_generator(folder_path, extensions, include_subfolders, include_folders)
            for name, is_folder in generator:
                if is_folder:
                    folder_names.append(name)
                else:
                    file_names.append(name)

            with open(save_path, 'w', encoding='utf-8') as f:
                if include_folders and folder_names:
                    f.write("==============================\n")
                    f.write(_("📁 Folder Names\n"))
                    f.write("==============================\n")
                    for name in folder_names:
                        f.write(name + "\n")
                    f.write("\n")
                f.write("==============================\n")
                f.write(_("📄 File Names\n"))
                f.write("==============================\n")
                for name in file_names:
                    f.write(name + "\n")
                f.write("\n")
                f.write("==============================\n")
                f.write(_("📊 Summary\n"))
                f.write("==============================\n")
                if include_folders:
                    f.write(_("Total Folders: {}\n").format(len(folder_names)))
                f.write(_("Total Files: {}\n").format(len(file_names)))

            result_content = ""
            if include_folders and folder_names:
                result_content += _("Total Folders: {}\n").format(len(folder_names))
            result_content += _("Total Files: {}\n").format(len(file_names)) + "\n"
            if include_folders and folder_names:
                result_content += _("Folders:\n") + "\n".join(folder_names) + "\n\n"
            result_content += _("Files:\n") + "\n".join(file_names)
            wx.CallAfter(self.result_text.SetValue, result_content)

            message = _("List saved to {}\n").format(save_path)
            if include_folders and folder_names:
                message += _("Total Folders: {}\n").format(len(folder_names))
            message += _("Total Files: {}").format(len(file_names))
            wx.CallAfter(wx.MessageBox, message, _("Completed"), wx.OK | wx.ICON_INFORMATION | wx.STAY_ON_TOP, self)
        except Exception as e:
            wx.CallAfter(wx.MessageBox, _("Error processing: {}").format(str(e)), _("Error"), wx.OK | wx.ICON_ERROR)

if __name__ == '__main__':
    app = wx.App()
    frame = FileCollectorFrame(None, title=_('File Name Collector'))
    app.MainLoop()