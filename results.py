from kivymd.uix.behaviors import CommonElevationBehavior, FakeRectangularElevationBehavior
from kivymd.uix.card import MDCard
from kivy.lang import Builder


Builder.load_string('''

<HeroResults>
    
    orientation: "vertical"
    size_hint: .5, None
    height: "90dp"
    elevation: 4
    radius: 5
    


    BoxLayout:  
        id: box
        size_hint: .9, 1
        orientation: "horizontal"
        
        BoxLayout:
            id: imageBox        
            size_hint: None, 1
            width: root.width / 1.7
            orientation: "horizontal"
                    
            Image:
                id: imageResult
                
                size_hint: None, 1
                size: imageBox.size
                radius: 16

        BoxLayout:
            id: infoBox
            size_hint: None, 1
            width: root.width / 2.3
            height: box.height
            orientation: "vertical"
            
            MDLabel:
                id: lModel
                text: "unk"
                bold: True
                adaptive_height: True
                padding: 5, 5
                font_style: "Caption"
                    
            MDLabel:
                id: lComp
                text: "C504"
                bold: True
                adaptive_height: True
                padding: 5, 5
                font_style: "Button"

            MDLabel:
                id: lConf
                text: "0.75"
                bold: True
                adaptive_height: True
                padding: 5, 5
                font_style: "Caption"


                    
                    
''')


class ElevationCard(FakeRectangularElevationBehavior, MDCard):
    pass




class HeroResults(ElevationCard):
    
    def set_image(self, image):
        self.ids.imageResult = image

    def set_comp(self, name):
        self.ids.lComp.text = name
    
    def set_model(self, model):
        self.ids.lModel.text = model

    def set_conf(self, conf):
        self.ids.lConf.text = conf

    def set_texture(self, texture):
        self.ids.imageResult.texture = texture

    def set_background(self, color):
        self.ids.box.md_bg_color = color