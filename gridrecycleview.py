from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.properties import StringProperty
from kivy.factory import Factory




KV = '''
<GridItem>
    size_hint: None, None
    size: "150dp", "150dp"

    BoxLayout:
        orientation: "vertical"
        AsyncImage:
            source: root.image_source
        Label:
            text: root.text

<MyRecycleView>:
    viewclass: "GridItem"
    RecycleGridLayout:
        cols: 3
        default_size: None, dp(48)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        spacing: dp(8)
'''

class GridItem(RecycleDataViewBehavior, BoxLayout):
    image_source = StringProperty()
    text = StringProperty()

    def refresh_view_attrs(self, rv, index, data):
        self.image_source = data["image_source"]
        self.text = data["text"]
        return super(GridItem, self).refresh_view_attrs(rv, index, data)


class MyRecycleView(RecycleView):
    def __init__(self, **kwargs):
        super(MyRecycleView, self).__init__(**kwargs)
        self.data = [
            {"image_source": "not-found-image.jpg", "text": "Image 1"},
            {"image_source": "not-found-image.jpg", "text": "Image 2"},
            {"image_source": "not-found-image.jpg", "text": "Image 3"},
            # Add more images here
        ]


class MyApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"
        return Builder.load_string(KV)

    def on_start(self):
        Builder.load_string(KV)
        Factory.register("GridItem", cls=GridItem)
        Factory.register("MyRecycleView", cls=MyRecycleView)

MyApp().run()
