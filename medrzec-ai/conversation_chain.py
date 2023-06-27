from langchain.chains import ConversationChain


class CleanConversationChain(ConversationChain):
    def prep_outputs(
        self,
        inputs: dict[str, str],
        outputs: dict[str, str],
        return_only_outputs: bool = False,
    ) -> dict[str, str]:
        outputs = {key: clean_message(value) for key, value in outputs.items()}
        return super().prep_outputs(inputs, outputs, return_only_outputs)


def clean_message(text: str) -> str:
    lines = []

    for line in text.splitlines():
        if line.startswith("Human:"):
            print("Fixed AI reply (included a human response)")
            break

        lines.append(line)

    return "\n".join(lines)
