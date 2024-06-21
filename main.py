import pygame
import flet as ft
import os

pygame.init()
pygame.mixer.init()

music_dir = os.path.join(os.path.expanduser('~'), "Music")

current_playing_song = None



class SongCurrent(ft.Container):
    def __init__(self) -> None:
        pass


class Song(ft.Container):
    def __init__(self, path: str) -> None:
        self.path = path

        super().__init__(
            bgcolor=ft.colors.BLACK,
            border_radius=20,
            height=60,
            padding=10,
            content=ft.Row(
                controls=[
                    ft.Text(
                        value=os.path.splitext(os.path.basename(path))[0],
                        size=17,
                        expand=True
                    ),
                    ft.IconButton(
                        icon=ft.icons.PLAY_CIRCLE,
                        icon_color=ft.colors.WHITE,
                        highlight_color=ft.colors.TRANSPARENT,
                        focus_color=ft.colors.TRANSPARENT,
                        hover_color=ft.colors.TRANSPARENT,
                        scale=1.2,
                        alignment=ft.alignment.center_right,
                        on_click=self.toggle_play_pause
                    ),
                ],
            )
        )
        
        self.state = ''

    def toggle_play_pause(self, e: None) -> None:
        global current_playing_song

        if current_playing_song and current_playing_song != self:
            current_playing_song.stop()
        
        if self.state == '':
            try:
                pygame.mixer.music.load(self.path)
                pygame.mixer.music.play()

                self.content.controls[1].icon = ft.icons.PAUSE_CIRCLE
                self.state = 'playing'
                current_playing_song = self
                self.update()
            except pygame.error as e:
                print(f"Error playing {self.path}: {e}")

        elif self.state == 'playing':
            try:
                pygame.mixer.music.pause()

                self.content.controls[1].icon = ft.icons.PLAY_CIRCLE
                self.state = 'paused'
                self.update()
            except pygame.error as e:
                print(f"Error pausing {self.path}: {e}")
        
        elif self.state == 'paused':
            try:
                pygame.mixer.music.unpause()

                self.content.controls[1].icon = ft.icons.PAUSE_CIRCLE
                self.state = 'playing'
                self.update()
            except pygame.error as e:
                print(f"Error unpausing {self.path}: {e}")

    def stop(self) -> None:
        try:
            pygame.mixer.music.stop()
            self.content.controls[1].icon = ft.icons.PLAY_CIRCLE
            self.state = ''
        except pygame.error as e:
            print(f"Error stopping {self.path}: {e}")
        
        self.update()


class Main(ft.View):
    def __init__(self, page: ft.Page) -> None:
        self.music_files = [os.path.join(music_dir, file) for file in os.listdir(music_dir) if file.endswith(('.mp3', '.wav'))]

        self.song_list = ft.Column()
        for file in self.music_files:
            song = Song(file) 
            self.song_list.controls.append(song)

        if current_playing_song:
            self.song_current = ft.Container(
                height=90,
                border_radius=30,
                padding= 10,
                bgcolor=ft.colors.BLACK,
                content=ft.Row(
                    alignment=ft.alignment.bottom_center,
                    controls=[
                        ft.Text(value=current_playing_song.path)
                    ]
                )
            )

            self.controls.append(self.song_current)
            self.update()
        

        super().__init__(
            route='/main',
            scroll=True,
            padding=20,
            controls=[self.song_list]
        )


def main(page: ft.Page) -> None:
    page.theme_mode = 'dark'
    
    def view_pop(view: ft.View) -> None:
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    def router(route) -> None:
        page.views.clear()
        page.views.append(
            Main(page)
        )

        if page.route == '/main/song':
            pass

        page.update()

    page.on_route_change = router
    page.on_view_pop = view_pop
    page.go(route='/main')
ft.app(target=main)
