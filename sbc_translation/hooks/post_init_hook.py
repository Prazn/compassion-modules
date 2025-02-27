import logging

from odoo import SUPERUSER_ID, api

logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    logger.info("SBC Translation Init Hook: create missing competences")

    # Update translation done
    cr.execute(
        """
            UPDATE correspondence SET translate_done = translate_date
            WHERE translate_date IS NOT NULL;
            UPDATE correspondence SET translate_date = write_date
            WHERE state = 'Global Partner translation queue'
            AND translate_date IS NULL;
        """
    )

    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        # Update correspondence competence
        for letter in env["correspondence"].search(
            [
                ("translation_competence_id", "=", False),
                ("src_translation_lang_id", "!=", False),
                ("translation_language_id", "!=", False),
            ]
        ):
            src = letter.src_translation_lang_id
            dst = letter.translation_language_id
            competence = env["translation.competence"].search(
                [("source_language_id", "=", src.id), ("dest_language_id", "=", dst.id)]
            )
            if not competence:
                competence = env["translation.competence"].create(
                    [{"source_language_id": src.id, "dest_language_id": dst.id}]
                )
            cr.execute(
                "UPDATE correspondence SET translation_competence_id = %s WHERE id = %s",
                [competence.id, letter.id],
            )
