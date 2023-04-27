from vocode.streaming.transcriber.deepgram_transcriber import DeepgramTranscriber
from vocode.streaming.models.synthesizer import ElevenLabsSynthesizerConfig
from vocode.streaming.models.message import BaseMessage
from vocode.streaming.models.agent import (
    ChatGPTAgentConfig,
    CutOffResponse,
    ChatGPTAgentConfig,
)
from vocode.streaming.models.transcriber import (
    DeepgramTranscriberConfig,
    PunctuationEndpointingConfig,
)
from vocode.helpers import create_microphone_input_and_speaker_output
from vocode.streaming.streaming_conversation import StreamingConversation
from vocode.streaming.agent.chat_gpt_agent import ChatGPTAgent
import asyncio
import logging
import signal
from dotenv import load_dotenv

from vocode.streaming.synthesizer.eleven_labs_synthesizer import ElevenLabsSynthesizer

load_dotenv()


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def main():
    microphone_input, speaker_output = create_microphone_input_and_speaker_output(
        streaming=True, use_default_devices=True
    )

    conversation = StreamingConversation(
        output_device=speaker_output,
        transcriber=DeepgramTranscriber(
            DeepgramTranscriberConfig.from_input_device(
                microphone_input, endpointing_config=PunctuationEndpointingConfig()
            )
        ),
        agent=ChatGPTAgent(
            ChatGPTAgentConfig(
                initial_message=BaseMessage(text="Hey, there!"),
                prompt_preamble="You are a helpful assistant.",
                generate_responses=True,
                cut_off_response=CutOffResponse(),
                allowed_idle_time_seconds=40,
            )
        ),
        synthesizer=ElevenLabsSynthesizer(
            ElevenLabsSynthesizerConfig.from_output_device(
                speaker_output,
                voice_id="YkFvMYSrlovAlkZ5nfxg",
                stability=0.1,
                similarity_boost=0.9
            ),
        ),
        logger=logger,
    )
    await conversation.start()
    print("Conversation started, press Ctrl+C to end")
    signal.signal(signal.SIGINT, lambda _0, _1: conversation.terminate())
    while conversation.is_active():
        chunk = microphone_input.get_audio()
        if chunk:
            conversation.receive_audio(chunk)
        await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(main())
