import os
import time
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.table import Table
from rich.live import Live
from rich import box

import config
from storage.call_db import CallDatabase
from state.call_state import CallState
from stt.mock import MockSTT
from tts.mock import MockTTS
from llm.mock import MockLLM
from controller.call_controller import CallController

console = Console()

def render_dashboard(state: CallState, transcript: list, status: str) -> Panel:
    """Renders the dashboard with state variables on the left and transcript on the right."""
    # Build state table
    state_table = Table(show_header=False, box=box.ROUNDED, expand=True)
    state_table.add_column("Key", style="cyan", width=15)
    state_table.add_column("Value", style="yellow")
    
    state_table.add_row("Caller Name", state.caller_name or "---")
    state_table.add_row("Callback No", state.callback_number or "---")
    state_table.add_row("Intent", state.intent or "---")
    state_table.add_row("Route", state.department or "PENDING")
    
    state_table.add_row("Request", state.request or "---")
    state_table.add_row("Callback Pref", state.callback_preference or "---")
    for key, value in state.details.items():
        state_table.add_row(key, value)
    state_table.add_row("Silence Count", str(state.silence_count))
    state_table.add_row("Clarify Fails", str(state.clarification_failures))

    # Build transcript text
    transcript_content = []
    for turn in transcript:
        sender = turn["sender"]
        text = turn["text"]
        if sender == "assistant":
            transcript_content.append(f"[bold green]AI Assistant:[/bold green] {text}")
        elif sender == "caller":
            transcript_content.append(f"[bold blue]Caller:[/bold blue] {text}")
        else:
            transcript_content.append(f"[dim grey]{text}[/dim grey]")
    
    transcript_text = "\n\n".join(transcript_content)

    # Set up layout
    layout = Layout()
    layout.split_row(
        Layout(name="left", ratio=2),
        Layout(name="right", ratio=3)
    )
    
    layout["left"].update(Panel(state_table, title="[bold cyan]Structured Call State[/bold cyan]"))
    layout["right"].update(Panel(transcript_text, title="[bold green]Live Transcript[/bold green]", padding=(1, 2)))

    # Main outer wrapper
    return Panel(
        layout,
        title=f"[bold white]AI Phone Assistant PoC[/bold white] — Status: [bold magenta]{status}[/bold magenta]",
        border_style="magenta",
        padding=(1, 1)
    )

def run_session(predefined_inputs: list = None, simulate_delays: bool = False, use_config: bool = False):
    """Runs either a scripted demo or a live microphone call."""
    if use_config:
        db = config.get_db()
        stt = config.get_stt()
        tts = config.get_tts()
        llm = config.get_llm()
    else:
        db = CallDatabase()
        stt = MockSTT(predefined_inputs=predefined_inputs)
        tts = MockTTS()
        llm = MockLLM()
        
    controller = CallController(llm=llm, db=db)

    # Welcome greeting
    greeting = controller.initialize_call()
    
    status = "SPEAKING"
    console.clear()
    console.print(render_dashboard(controller.state, controller.transcript, status))
    tts.speak(greeting)
    
    if simulate_delays:
        time.sleep(1.5)

    while controller.active:
        status = "LISTENING"
        console.clear()
        console.print(render_dashboard(controller.state, controller.transcript, status))
        
        # Get caller speech (either from predefined test array, mic recording, or interactive typing)
        if use_config and not isinstance(stt, MockSTT):
            from audio.recorder import AudioRecorder
            recorder = AudioRecorder(vad=config.get_vad())
            console.print("\n[bold yellow]Speak now... (Silence will end response)[/bold yellow]")
            audio_path = recorder.record_until_silence()
            if audio_path:
                caller_text = stt.transcribe(audio_path)
                recorder.cleanup()
            else:
                caller_text = ""
        else:
            caller_text = stt.transcribe()
        
        status = "THINKING"
        console.clear()
        console.print(render_dashboard(controller.state, controller.transcript, status))
        if simulate_delays:
            time.sleep(1.0)
            
        # Controller decides next steps
        reply = controller.process_caller_input(caller_text)
        
        status = "SPEAKING"
        console.clear()
        console.print(render_dashboard(controller.state, controller.transcript, status))
        tts.speak(reply)
        
        if simulate_delays:
            time.sleep(1.5)

    # Print final completion state
    console.clear()
    console.print(render_dashboard(controller.state, controller.transcript, "DISCONNECTED"))
    
    final_summary = llm.summarize(controller.state, controller.transcript)
    console.print("\n[bold green]================ CALL COMPLETE ================ [/bold green]")
    console.print(f"[bold cyan]ROUTE DEPARTMENT:[/bold cyan] {controller.state.department or 'HUMAN'}")
    console.print(Panel(final_summary, title="[bold yellow]Generated Callback/Intake Summary Card[/bold yellow]"))
    input("\nPress Enter to return to main menu...")

def main_menu():
    while True:
        console.print(Panel(
            "CallAssist — Phone Intake Demo\n\n"
            "1) Sales inquiry demo\n"
            "2) Support message demo\n"
            "3) Appointment request demo\n"
            "4) Interactive text demo\n"
            "5) Live microphone session\n"
            "6) Exit", title="Main Menu"))
        choice = input("Enter choice (1-6): ").strip()
        demos = {
            "1": ["I'd like a quote for your services.", "My name is Alex Rivera", "303-555-0123"],
            "2": ["I need support with a problem with my order.", "My name is Sam Lee", "303-555-0124"],
            "3": ["I'd like to schedule an appointment.", "My name is Taylor Morgan", "303-555-0125"],
        }
        if choice in demos:
            run_session(predefined_inputs=demos[choice])
        elif choice == "4":
            run_session()
        elif choice == "5":
            run_session(use_config=True)
        elif choice == "6":
            break
        else:
            console.print("Please choose 1-6.")

if __name__ == "__main__":
    main_menu()
