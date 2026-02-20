from __future__ import annotations

from typing import List, Optional, Dict, Any

from core.models import PayloadTemplate
from core.registry import get_registry, RegistryError
from exporters.json_exporter import JSONExporter
from exporters.txt_exporter import TXTExporter
from transforms.encoder import encode_payload
from transforms.obfuscator import obfuscate_payload


class PipelineError(RuntimeError):
    pass


class PayloadPipeline:

    def __init__(self) -> None:
        self.registry = get_registry()

    # ----------------------------
    # Generation
    # ----------------------------

    def generate(
        self,
        module: str,
        *,
        db_type: Optional[str] = None,
        os_type: Optional[str] = None,
        context: Optional[str] = None,
    ) -> List[PayloadTemplate]:

        try:
            return self.registry.generate(
                module,
                db_type=db_type,
                os_type=os_type,
                context=context,
            )
        except Exception as e:
            raise PipelineError(f"Generation failed: {e}") from e

    # ----------------------------
    # Encoding
    # ----------------------------

    def apply_encoding_to_all(
        self,
        items: List[PayloadTemplate],
        method: str,
    ) -> List[PayloadTemplate]:

        out: List[PayloadTemplate] = []

        for item in items:
            try:
                new_payload = encode_payload(item.payload, method=method)
            except Exception as e:
                raise PipelineError(
                    f"Encoding '{method}' failed: {e}"
                ) from e

            new_item = item.clone_with_updates(payload=new_payload)
            new_item.add_encoding(method)
            out.append(new_item)

        return out

    # ----------------------------
    # Obfuscation
    # ----------------------------

    def apply_obfuscation_to_all(
        self,
        items: List[PayloadTemplate],
        technique: str,
    ) -> List[PayloadTemplate]:

        out: List[PayloadTemplate] = []

        for item in items:
            try:
                new_payload = obfuscate_payload(
                    item.payload,
                    mode=technique,
                )
            except Exception as e:
                raise PipelineError(
                    f"Obfuscation '{technique}' failed: {e}"
                ) from e

            new_item = item.clone_with_updates(payload=new_payload)
            new_item.add_obfuscation(technique)
            out.append(new_item)

        return out

    # ----------------------------
    # Run
    # ----------------------------

    def run(
        self,
        *,
        module: str,
        db_type: Optional[str] = None,
        os_type: Optional[str] = None,
        context: Optional[str] = None,
        encoding: Optional[str] = None,
        obfuscation: Optional[str] = None,
        export_format: Optional[str] = None,
        output_path: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> List[PayloadTemplate]:

        items = self.generate(
            module=module,
            db_type=db_type,
            os_type=os_type,
            context=context,
        )

        if encoding:
            items = self.apply_encoding_to_all(items, encoding)

        if obfuscation:
            items = self.apply_obfuscation_to_all(items, obfuscation)

        if export_format:

            if not output_path:
                raise PipelineError("Output path required when export_format is set.")

            if export_format == "json":
                exporter = JSONExporter()
                exporter.export(items, output_path, meta=meta)

            elif export_format == "txt":
                exporter = TXTExporter()
                exporter.export(items, output_path, meta=meta)

            else:
                raise PipelineError(f"Unsupported export format '{export_format}'.")

        return items


# Convenience wrapper
def run_pipeline(**kwargs) -> List[PayloadTemplate]:
    return PayloadPipeline().run(**kwargs)
