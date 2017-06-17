import base64 as _b64
import PIL.Image as _image
import io as _io

close_icon = 'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAQAAAC1+jfqAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAAAmJLR0QAAKqNIzIAAAAJcEhZcwAADdcAAA3XAUIom3gAAAAHdElNRQfhBg0PLB09jQ+wAAAAnklEQVQoz42RuxHCMBBEnzAdkChSKIpxB3TgTB3gHi4g8zgjVEQzEJE5oQYR2DoxjH8v0Ehzq7m9PUPGc8FhgMSbO09+MAQEp2+HEDCl3FPzT02fJWGmPErC2FtYQvDQau+IBcAS1csVOtVbInY6M92xeGWg4QY0DGW+A5tstNhhsoxZ6b98E3zFhzMnXkBSQZqCMjx2Rb26rJLCwrq/pi4oZuXrgZ8AAAAldEVYdGRhdGU6Y3JlYXRlADIwMTctMDYtMTNUMTU6NDQ6MjkrMDI6MDBotB6VAAAAJXRFWHRkYXRlOm1vZGlmeQAyMDE3LTA2LTEzVDE1OjQ0OjI5KzAyOjAwGemmKQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAAASUVORK5CYII='
edit_icon = 'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAQAAAC1+jfqAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAAAmJLR0QAAKqNIzIAAAAJcEhZcwAADdcAAA3XAUIom3gAAAAHdElNRQfhBg0PLS/sQW9xAAAA5klEQVQoz23Ruy6DAQCG4ef/K44llEgMIhaJQdgExSASdRhrkLgXLkBMHSy6SURMDh260SBiaLgAC5FIdKgqo6GRUv+3Pu/2BaI3Zl23kkw0Jx3LatZnO4zkLWV5e8oSQQSn3es1Km/RUyyCi/aNqJrUJRP+408vyHozaNdD0MBVF3KWDJhwpEDTH/5QkJMyr63G9SApreLKuWWzdf4JanztzIoZ7XUmRNKGdzdOrZrW8ZsJtdqRUHFizZT4XyYwZ8irBSVxnY1MzKYTz6pSOGxkQuN6tOg37OA/E3h0p+jSra+oY78BqEZCMVdOKtgAAAAldEVYdGRhdGU6Y3JlYXRlADIwMTctMDYtMTNUMTU6NDU6NDcrMDI6MDARJgdxAAAAJXRFWHRkYXRlOm1vZGlmeQAyMDE3LTA2LTEzVDE1OjQ1OjQ3KzAyOjAwYHu/zQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAAASUVORK5CYII='
app_icon = 'iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAMAAAD04JH5AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAMAUExURUJCDU9PEFVUEWtbFW1tFX9xGXt7GKI/IIVQGp5FH5dVHpFcHZpWHopnG49qHIl0G4t6G5RrHZN1HZJ8HZ51H5t8Hp52IKNCIKlGIq5II7JKJKB2IKd4IbZiJLFrI7pnJb9qJv8BM/8MM/8QM/8bM/8jM/8sM/81M/88M8J2J8N/J/9DM/9MM/9TM/9aM/9jM/9rM/9zM/97M4WEGoqDG42KG5WBHZSLHZuDHpuNHpSRHZuTHpuaHp+NIJ+VIJqSKZ6dIKGEIKSKIKKVIKObIKuRIquaIqCRMK6eNLaAJL2NJrKTI7WbJLmXJbmbJaSiIKujIqyqIrSjJLOqI7qkJbusJbOjNbSyJLyzJby6JZmTT5qVaK6ge7KifLimfb2ofr+wf8eIKMuLKMuUKNKCKt6OLNWbKsKjJsemKMOrJsuqKMOyJ8S6Jse7KM+zKcq8KNOkKtStKtuhK9G0KtG6KduyK9m9K+WILvGPMP+DM/+LM/ecMf6TMv6bMuSlLeqqLuOzLeO9Luu1L+u7L/+jM/6rM/G1MPK9MP+yM/67MsOsf8TEJ8zDKMvKKM7CO9PFKtPLKtvBK9vMK9XSKtrQK9rRLNnWK9rVLN7QLN7VLNzZK+TGLePMLe3CL+vKLu7JMOHULePaLerTLuvbLuDaM+7WMO/dMPLDMPTNMP7EMv7KMvPUMPTaMP7TM/7bMuThLeziL+rqLu7kMO/qMPTkMPTqMP7jMv7rMvTzMP7zMv77M//9PP3cQvPrTP/lRf/jTv/kX//qX//1RP/2T//8Rf/9Tv/2U//1X/79Vf/7Xf/iev71bf/7Y//4av/2cf/0ef/7cf/7ecuygdO4g9u9hPeniv+njP2ri/K2ifK4if+wjOLChenDh+3BiP/AjP/XjO/njf/ljP/vjP/jlf70hP72iv/4hP/9i//0lf/0nf/6lf/8nP/jpP/mr//ns//vtP//ov/6r//3uP/9tP/6uP78wv/+yv/y1f/70//52+zs6f/+4/797f7+9f///gAAAAjEtkwAAAEAdFJOU////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////wBT9wclAAAACXBIWXMAAA7DAAAOwwHHb6hkAAAAGXRFWHRTb2Z0d2FyZQBwYWludC5uZXQgNC4wLjEwrQoKwAAAEJBJREFUeF61mwt0HFUdxisiiqI8KuL70FaaakublLYhD7Bp0qrAIQkBm/o8ilILwQA2SuMuzwR3IbUhBU4ptTaNWjbtpgWandypD6ggVAQsInAAwSJQan1VSwFtc/y+///O7Ow22Wyyw5eSnZ2Zne833/3fO3dmw7jbjeM4KVGfKukJy1iLzUbkZqpyMBSNMwGAbIQAAByN/Piqf+0AZY8zZgHAumd6U3grABqAJ+vvLrxLXuxxxqxxjkkxALWnrHsvAJIZTSBKpzBwxABf7HHGrHFoAfpbAutOe0gTMBkRpFuhcsA9MgSAHiSQEYFYi/AGGzL9RQowcNRR9SEAVBsn5fjlF6wBvsU2axqQ+ksEIQDU9TMBvwmyE3ACCWDBLisAzj8EgO4LvG6oCJA1z65ALFNYsnWwKJQETOVWAAQQxFt+ZwEoAX5zmQB3MQJ7nDFrnOkvw2FJAEfxhvkQCYizEFD0RwSrQwDYu7ejgceVCALtIO1PTzHUsycmXz2C5ctDABgcNOtq9NwyELBkrTwArNCVlsp1O8NIAACmqVMItBLSAAyARvxFX67yI5AQKmvDAHjllZc+3a8OHoE42QRU3OqJu2IV+8LmRTt27DhkjzUmAQD6RYU1sS72/L0EdD24/GS8DAYWIocQAH7d0Ynj0Sd9olKCvoQBBLKFwjpemCrDAXigv5EmsNFWoAuvQlkJiLgNG4QAdbgoHIDNHX6xKwEX/AB0pQXwEBTOresPBWDlShxLrSjJ3/Y2XUt/ThAwRdABQgBYh+WhAHTexga1CVh/tbdrcdrq7ycgG6Hli/bu3XtQDjMWeU2AMY1SNytrL2vg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'

def to_image(string):
    b = _b64.b64decode(string)
    return _image.open(_io.BytesIO(b))

def alpha_to_bw(image):
    image = image.convert("RGBA")
    
    pixels = image.load()
    for y in range(image.height):
        for x in range(image.width):
            r,g,b,a = pixels[x,y]
            if a > 0:
                a = 255 - a
                pixels[x,y] = (a,a,a,255)
            else:
                pixels[x,y] = (255,255,255,255)

    return image.convert("L")

def invert_alpha(image):
    image = image.convert("RGBA")

    pixels = image.load()
    for y in range(image.height):
        for x in range(image.width):
            r,g,b,a = pixels[x,y]
            pixels[x,y] = r,g,b,255-a

    return image

close_icon = to_image(close_icon).convert("RGBA")
edit_icon = to_image(edit_icon).convert("RGBA")
app_icon = to_image(app_icon)