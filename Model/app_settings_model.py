from dataclasses import dataclass, field
from typing     import ClassVar, Dict
from pathlib    import Path
import json
import copy

@dataclass
class SoundTrack:
    enabled: bool  = False
    volume:  float = 0.5

@dataclass
class ThemeSettings:
    current_theme: str = "Forest Light"

@dataclass
class SoundSettings:
    master_volume:      float = 0.6
    auto_play_on_focus: bool  = True
    white_noise: Dict[str, SoundTrack] = field(default_factory=lambda: {
        "rain":        SoundTrack(enabled=False,  volume=0.7),
        "forest_wind": SoundTrack(enabled=False, volume=0.5),
        "ocean":       SoundTrack(enabled=False, volume=0.5),
        "fireplace":   SoundTrack(enabled=False, volume=0.5),
        "cafe":        SoundTrack(enabled=False, volume=0.5),
    })

    def effective_volume(self, name: str) -> float:
        t = self.white_noise[name]
        return self.master_volume * t.volume if t.enabled else 0.0

@dataclass
class TimerSettings:
    work_duration:    int  = 25 * 60
    short_break:      int  = 5  * 60
    long_break:       int  = 15 * 60
    pomo_until_break: int  = 4
    auto_start_break: bool = False
    auto_start_focus: bool = False

@dataclass
class AppSettings:
    timer: TimerSettings = field(default_factory=TimerSettings)
    sound: SoundSettings = field(default_factory=SoundSettings)
    theme: ThemeSettings = field(default_factory=ThemeSettings)

    PATH: ClassVar[Path] = Path("data/settings.json")

    # ─read values from json 
    @classmethod
    def load(cls) -> "AppSettings":
        if not cls.PATH.exists():
            return cls()

        data = json.loads(cls.PATH.read_text())
        c    = data.get("timer", {})
        s    = data.get("sound", {})
        raw  = s.get("white_noise", {})

        defaults = SoundSettings().white_noise
        tracks = {
            name: SoundTrack(
                enabled = raw.get(name, {}).get("enabled", d.enabled),
                volume  = raw.get(name, {}).get("volume",  d.volume),
            )
            for name, d in defaults.items()
        }

        return cls(
            timer = TimerSettings(
                work_duration    = c.get("work_duration",    25*60),
                short_break      = c.get("short_break",       5*60),
                long_break       = c.get("long_break",        15*60),
                pomo_until_break = c.get("pomo_until_break",  4),
                auto_start_break = c.get("auto_start_break",  False),
                auto_start_focus = c.get("auto_start_focus",  False),
            ),
            sound = SoundSettings(
                master_volume      = s.get("master_volume",      0.6),
                auto_play_on_focus = s.get("auto_play_on_focus", True),
                white_noise        = tracks,
            ),
            theme = ThemeSettings(
                current_theme = data.get("theme", {}).get("current_theme", "Forest Light")
            )
        )

    # write to the json file 
    def save(self) -> None:
        self.PATH.parent.mkdir(parents=True, exist_ok=True)
        self.PATH.write_text(json.dumps(self._to_dict(), indent=2))
    # helper function returns dict
    def _to_dict(self) -> dict:
        return {
            "timer": {
                "work_duration":    self.timer.work_duration,
                "short_break":      self.timer.short_break,
                "long_break":       self.timer.long_break,
                "pomo_until_break": self.timer.pomo_until_break,
                "auto_start_break": self.timer.auto_start_break,
                "auto_start_focus": self.timer.auto_start_focus,
            },
            "sound": {
                "master_volume":      self.sound.master_volume,
                "auto_play_on_focus": self.sound.auto_play_on_focus,
                "white_noise": {
                    name: {"enabled": t.enabled, "volume": t.volume}
                    for name, t in self.sound.white_noise.items()
                }
            },
            "theme": {
                "current_theme": self.theme.current_theme
            }
        }

    # ── update helpers ──
    def update(self, section: str, field: str, value) -> None:
        setattr(getattr(self, section), field, value)
        self.save()

    def update_track(self, name: str, field: str, value) -> None:
        setattr(self.sound.white_noise[name], field, value)
        self.save()

    def clone(self) -> "AppSettings":
        return copy.deepcopy(self)
