import pygame
import flet as ft
import os

pygame.init()
pygame.mixer.init()

music_dir = "/home/misn/Music"

class Main(ft.View):
    def __init__(self, page) -> None:
        self.page = page
        self.music_files = [os.path.join(music_dir, file) for file in os.listdir(music_dir) if file.endswith(('.mp3', '.wav'))]

        self.song_list = ft.Column()
        for file in self.music_files:
            song = self.Song(file) 
            self.song_list.controls.append(song)

        self.current_song_text = ft.Text(value="No song playing", size=18)
        self.progress_bar = ft.ProgressBar(width=500)

        self.song_current_container = ft.Container(
            height=90,
            border_radius=30,
            padding=10,
            bgcolor=ft.colors.BLACK,
            content=ft.Column(
                controls=[
                    self.current_song_text,
                    self.progress_bar,
                ],
                alignment=ft.alignment.bottom_center
            ),
            alignment=ft.alignment.bottom_center
        )

        super().__init__(
            route='/main',
            scroll=True,
            padding=20,
            controls=[self.song_list, self.song_current_container]
        )

        self.current_playing_song = None

    class Song(ft.Container):
        def __init__(self, path) -> None:
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
            current_playing_song = Main().current_playing_song

            if current_playing_song and current_playing_song != self:
                current_playing_song.stop()
            
            if self.state == '':
                try:
                    pygame.mixer.music.load(self.path)
                    pygame.mixer.music.play()

                    self.content.controls[1].icon = ft.icons.PAUSE_CIRCLE
                    self.state = 'playing'
                    current_playing_song = self
                    current_playing_song.update_current_song(os.path.basename(self.path))
                    current_playing_song.bring_to_front(current_playing_song)
                    current_playing_song.update_progress_bar()
                except pygame.error as e:
                    print(f"Error playing {self.path}: {e}")

            elif self.state == 'playing':
                try:
                    pygame.mixer.music.pause()

                    self.content.controls[1].icon = ft.icons.PLAY_CIRCLE
                    self.state = 'paused'
                except pygame.error as e:
                    print(f"Error pausing {self.path}: {e}")
            
            elif self.state == 'paused':
                try:
                    pygame.mixer.music.unpause()

                    self.content.controls[1].icon = ft.icons.PAUSE_CIRCLE
                    self.state = 'playing'
                    current_playing_song.update_progress_bar()
                except pygame.error as e:
                    print(f"Error unpausing {self.path}: {e}")

        def stop(self) -> None:
            try:
                pygame.mixer.music.stop()
                self.content.controls[1].icon = ft.icons.PLAY_CIRCLE
                self.state = ''
            except pygame.error as e:
                print(f"Error stopping {self.path}: {e}")

    def update_current_song(self, song_name: str) -> None:
        self.current_song_text.value = song_name
        self.progress_bar.value = 0
        self.update()

    def update_progress_bar(self) -> None:
        if self.current_playing_song and self.current_playing_song.state == 'playing':
            pos = pygame.mixer.music.get_pos() / 1000
            song_length = pygame.mixer.Sound(self.current_playing_song.path).get_length()
            self.progress_bar.value = pos / song_length if song_length > 0 else 0
            self.page.call_later(1000, self.update_progress_bar)

    def bring_to_front(self, control) -> None:
        if control in self.controls:
            self.controls.remove(control)
            self.controls.append(control)
            self.update()

def main(page: ft.Page) -> None:
    def view_pop(view: ft.View) -> None:
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    def router(route) -> None:
        page.views.clear()
        main_view = Main(page)
        page.views.append(main_view)

        page.update()

    page.theme_mode = 'dark'
    page.on_route_change = router
    page.on_view_pop = view_pop
    page.go(route='/main')

ft.app(target=main)