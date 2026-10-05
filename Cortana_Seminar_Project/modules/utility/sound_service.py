from pathlib import Path
import pygame as sound_machine

_cortana_voicelines: dict[str, Path] = {
    "apologize": Path(__file__).resolve().parents[2] / "sounds" / "cortana" / "right_sorry.wav",
    "compliment": Path(__file__).resolve().parents[2] / "sounds" / "cortana" / "nice_work.wav",

    "gladly": Path(__file__).resolve().parents[2] / "sounds" / "cortana" / "gladly.wav",
    "its_been_an_honor": Path(__file__).resolve().parents[2] / "sounds" / "cortana" / "its_been_an_honor.wav",

    "alright": Path(__file__).resolve().parents[2] / "sounds" / "cortana" / "alright.wav",
    "alright_2": Path(__file__).resolve().parents[2] / "sounds" / "cortana" / "alright_2.wav",

    "i_dont_think_so": Path(__file__).resolve().parents[2] / "sounds" / "cortana" / "i_dont_think_so.wav",
    "miss_me": Path(__file__).resolve().parents[2] / "sounds" / "cortana" / "so_you_did_miss_me.wav",

    "cutting_it_close": Path(__file__).resolve().parents[2] / "sounds" / "cortana" / "were_cutting_it_close.wav",
    "with_all_due_respect": Path(__file__).resolve().parents[2] / "sounds" / "cortana" / "with_all_due_respect_sir.wav",

    "something_on_your_mind": Path(__file__).resolve().parents[2] / "sounds" / "cortana" / "something_on_your_mind.wav",
    "efficient": Path(__file__).resolve().parents[2] / "sounds" / "cortana" / "just_trying_to_be_efficient.wav",

    "use_my_help": Path(__file__).resolve().parents[2] / "sounds" / "cortana" / "you_could_use_my_help.wav",
    "you_sure": Path(__file__).resolve().parents[2] / "sounds" / "cortana" / "you_sure_thats_a_good_idea.wav",

    "i_think_we_both_know": Path(__file__).resolve().parents[2] / "sounds" / "cortana" / "i_think_we_both_know.wav",
    "down_here_chief": (Path(__file__).resolve().parents[2] / "sounds" / "cortana" / "down_here_chief.wav"),
    
    "generic_1": Path(__file__).resolve().parents[2] / "sounds" / "cortana" / "alright.wav",
    "generic_2": Path(__file__).resolve().parents[2] / "sounds" / "cortana" / "gladly.wav",
}

sound_machine.mixer.init()

def play_voiceline(voiceline: str = "generic_1", volume: int = .3):
    sound_effect = sound_machine.mixer.Sound(str(_cortana_voicelines.get(voiceline)))
    sound_effect.set_volume(.3 if voiceline != "cutting_it_close" else volume if volume is not None else .1); sound_effect.play()

def play_sfx(sound: str = "generic", volume: int = .3):
    sound += ".wav"; sound_effect = sound_machine.mixer.Sound(str(Path(__file__).resolve().parents[2] / "sounds" / "interface" / sound))
    sound_effect.set_volume(volume if volume is not None else .3); sound_effect.play()
    