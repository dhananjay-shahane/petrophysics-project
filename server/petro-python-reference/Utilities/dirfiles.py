from kivy.uix.filechooser import FileChooserListView

class CustomFileChooser(FileChooserListView):
    def __init__(self, **kwargs):
        super(CustomFileChooser, self).__init__(**kwargs)
        self.filters = ['*.png', '*.jpg', '*.gif']
    def on_file_select(selection):
        if selection:
            selected_file = selection[0]
            print(f'You have selected: {selected_file}')