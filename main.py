import pygame
import flet as ft
import os
import time
import threading

pygame.init()
pygame.mixer.init()

music_dir = os.path.join(os.path.expanduser('~'), "Music")

current_playing_song = None
current_playing_index = -1

class Navigation(ft.NavigationBar):
    def __init__(self) -> None:
        super().__init__(
            
        )

class SongCurrent(ft.Container):
    def __init__(self, main_view) -> None:
        self.main_view = main_view
        self.current_song_name = ft.Text(value="", size=20, text_align=ft.TextAlign.CENTER)
        self.progress_bar = ft.Slider(min=0, max=1, height=15, on_change=self.seek)
        self.elapsed_time_text = ft.Text(value="00:00", size=14)
        self.total_time_text = ft.Text(value="00:00", size=14)
        self.volume_slider = ft.Slider(min=0, max=1, value=1, width=150, height=10, on_change=self.change_volume)
        self.volume_icon = ft.Icon(
            name=ft.icons.VOLUME_UP,
            color=ft.colors.WHITE
        )
        self.play_pause_button = ft.IconButton(
            icon=ft.icons.PAUSE_CIRCLE,
            icon_color=ft.colors.WHITE,
            on_click=self.toggle_play_pause
        )
        self.next_button = ft.IconButton(
            icon=ft.icons.SKIP_NEXT,
            icon_color=ft.colors.WHITE,
            on_click=self.next_track
        )
        self.prev_button = ft.IconButton(
            icon=ft.icons.SKIP_PREVIOUS,
            icon_color=ft.colors.WHITE,
            on_click=self.prev_track
        )

        super().__init__(
            visible=False,
            bgcolor=ft.colors.with_opacity(0.7, ft.colors.BLACK),
            border_radius=10,
            padding=10,
            content=ft.Column(
                controls=[
                    self.current_song_name,
                    ft.Row(
                        controls=[
                            self.elapsed_time_text,
                            self.progress_bar,
                            self.total_time_text
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    ft.Row(
                        controls=[
                            self.prev_button,
                            self.play_pause_button,
                            self.next_button,
                            self.volume_icon,
                            self.volume_slider
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER
            )
        )

    def update_current_song(self, song_name: str, is_playing: bool, total_time: float) -> None:
        self.current_song_name.value = song_name
        self.play_pause_button.icon = ft.icons.PAUSE_CIRCLE if is_playing else ft.icons.PLAY_CIRCLE
        self.total_time_text.value = self.format_time(total_time)
        self.update()

    def update_progress(self, progress: float, elapsed_time: float) -> None:
        progress = max(0, min(progress, 1))  # Clamp progress to [0, 1]
        self.progress_bar.value = progress
        
        self.elapsed_time_text.value = self.format_time(elapsed_time)
        
        self.update()

    def seek(self, e: ft.ControlEvent) -> None:
        if current_playing_song and current_playing_song.state == 'playing':
            seek_position = e.control.value * current_playing_song.song_length
            pygame.mixer.music.set_pos(seek_position)
            current_playing_song.start_time = time.time() - seek_position

    def change_volume(self, e: ft.ControlEvent) -> None:
        pygame.mixer.music.set_volume(e.control.value)

    def toggle_play_pause(self, e: None) -> None:
        if current_playing_song:
            current_playing_song.toggle_play_pause(None)
            self.play_pause_button.icon = (
                ft.icons.PLAY_CIRCLE if current_playing_song.state == 'paused' else ft.icons.PAUSE_CIRCLE
            )
            self.update()

    def next_track(self, e: None) -> None:
        self.main_view.play_next_song()

    def prev_track(self, e: None) -> None:
        self.main_view.play_prev_song()

    def format_time(self, seconds: float) -> str:
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02}:{seconds:02}"

class Song(ft.Container):
    def __init__(self, path: str, song_current: SongCurrent, main_view, index: int) -> None:
        self.path = path
        self.song_current = song_current
        self.main_view = main_view
        self.index = index

        super().__init__(
            bgcolor=ft.colors.BLACK,
            border_radius=15,
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
        self.start_time = 0
        self.song_length = 0
        self.pause_time = 0

    def toggle_play_pause(self, e: None) -> None:
        global current_playing_song
        global current_playing_index

        if current_playing_song and current_playing_song != self:
            current_playing_song.stop()
        
        if self.state == '':
            try:
                pygame.mixer.music.load(self.path)
                pygame.mixer.music.play()

                self.song_length = pygame.mixer.Sound(self.path).get_length()
                self.start_time = time.time()

                self.content.controls[1].icon = ft.icons.PAUSE_CIRCLE
                self.state = 'playing'
                current_playing_song = self
                current_playing_index = self.index

                song_name = os.path.splitext(os.path.basename(self.path))[0]
                self.song_current.update_current_song(song_name, True, self.song_length)
                self.song_current.visible = True
                self.song_current.update()
                self.main_view.update()
                
                self.update()
            except pygame.error as e:
                print(f"Error playing {self.path}: {e}")

        elif self.state == 'playing':
            try:
                pygame.mixer.music.pause()
                self.pause_time = time.time()

                self.content.controls[1].icon = ft.icons.PLAY_CIRCLE
                self.state = 'paused'
                self.update()
            except pygame.error as e:
                print(f"Error pausing {self.path}: {e}")
        
        elif self.state == 'paused':
            try:
                pygame.mixer.music.unpause()
                self.start_time += time.time() - self.pause_time

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
            self.song_current.visible = False
            self.song_current.update()
            self.main_view.update()
        except pygame.error as e:
            print(f"Error stopping {self.path}: {e}")
        
        self.update()

    def get_progress(self) -> float:
        if self.state == 'playing':
            elapsed_time = time.time() - self.start_time
            progress = elapsed_time / self.song_length
            return progress, elapsed_time
        elif self.state == 'paused':
            elapsed_time = self.pause_time - self.start_time
            progress = elapsed_time / self.song_length
            return progress, elapsed_time
        return 0.0, 0.0


class Main(ft.View):
    def __init__(self, page: ft.Page) -> None:
        self.music_files = [os.path.join(music_dir, file) for file in os.listdir(music_dir) if file.endswith(('.mp3', '.wav'))]
        
        self.song_current = SongCurrent(self)
        self.song_list = ft.Container(height=850, content=ft.Column(scroll=True))

        self.songs = []
        for index, file in enumerate(self.music_files):
            song = Song(file, self.song_current, self, index)
            self.songs.append(song)
            self.song_list.content.controls.append(song)

        super().__init__(
            route='/main',
            padding=20,
            controls=[self.song_list, self.song_current]
        )

        self.update_progress_thread = threading.Thread(target=self.update_progress)
        self.update_progress_thread.daemon = True
        self.update_progress_thread.start()

    def update_progress(self) -> None:
        while True:
            if current_playing_song:
                progress, elapsed_time = current_playing_song.get_progress()
                self.song_current.update_progress(progress, elapsed_time)

                # Check if the current song has finished
                if progress >= 1.0:
                    # Play the next song automatically
                    self.play_next_song()

            time.sleep(1)

    def play_next_song(self) -> None:
        global current_playing_index
        if current_playing_index < len(self.songs) - 1:
            self.songs[current_playing_index + 1].toggle_play_pause(None)
        else:
            # If at the end of the list, loop back to the first song
            self.songs[0].toggle_play_pause(None)

    def play_prev_song(self) -> None:
        global current_playing_index
        if current_playing_index > 0:
            self.songs[current_playing_index - 1].toggle_play_pause(None)


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
