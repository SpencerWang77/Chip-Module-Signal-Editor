"""Central Qt stylesheet for the ESWIN register editor."""

STYLE_SHEET = """
* {
    font-family: "Avenir Next", "Segoe UI", sans-serif;
    color: #17343D;
}
QMainWindow, QStackedWidget, #pageBody, #editorBody, #rowContainer,
#moduleContainer, #editorContentStack, #uploadScroll {
    background: #F4F6F3;
}
#uploadScroll > QWidget > QWidget { background: #F4F6F3; }
#topBar {
    background: #FFFFFF;
    border-bottom: 1px solid #DEE6E4;
}
#brandName {
    font-size: 18px;
    font-weight: 700;
    letter-spacing: -0.4px;
    color: #112C36;
}
#stepLabel, #headerFile {
    color: #71858B;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.7px;
}
#eyebrow, #summaryTitle {
    color: #20A781;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.6px;
}
#pageTitle {
    color: #112C36;
    font-size: 38px;
    font-weight: 700;
    letter-spacing: -1.1px;
}
#pageIntro {
    color: #60767C;
    font-size: 15px;
}
#mutedText, #rowSecondary {
    color: #7B8E93;
    font-size: 11px;
}
#dropZone {
    background: #FCFDFB;
    border: 2px dashed #AFC9C1;
    border-radius: 18px;
}
#dropZone[dragging="true"] {
    background: #ECF9F4;
    border-color: #20B88A;
}
#fileIcon {
    background: #E6F7F1;
    border: 1px solid #BFE8DA;
    border-radius: 11px;
    color: #168063;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1px;
}
#dropTitle {
    color: #183A43;
    font-size: 18px;
    font-weight: 650;
}
QPushButton {
    min-height: 34px;
    padding: 0 16px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 600;
}
#primaryButton {
    background: #173E48;
    color: white;
    border: 1px solid #173E48;
}
#primaryButton:hover { background: #0F3038; }
#primaryButton:pressed { background: #09242B; }
#secondaryButton {
    background: #FFFFFF;
    color: #294750;
    border: 1px solid #C9D6D3;
}
#secondaryButton:hover { border-color: #20B88A; color: #14785E; }
#secondaryButton:disabled { color: #A8B4B5; background: #F1F3F2; border-color: #DDE3E1; }
#textButton {
    color: #168063;
    background: transparent;
    border: none;
    padding: 0 4px;
}
#textButton:hover { color: #0D5D48; }
#requirementsCard {
    background: #EEF2F0;
    border: 1px solid #DCE5E1;
    border-radius: 11px;
}
#rulesInfoButton {
    color: #FFFFFF;
    background: #168063;
    border: 1px solid #168063;
    border-radius: 15px;
    font-family: "Georgia", serif;
    font-size: 15px;
    font-weight: 800;
    padding: 0;
}
#rulesInfoButton:hover, #rulesInfoButton:focus {
    color: #0F624E;
    background: #D9F2E9;
    border-color: #49B493;
}
#rulesTitle {
    color: #173E48;
    font-size: 12px;
    font-weight: 750;
}
#rulesHoverHint {
    color: #168063;
    background: #DDF4EB;
    border-radius: 7px;
    padding: 4px 7px;
    font-size: 8px;
    font-weight: 800;
    letter-spacing: 0.8px;
}
#rulesDetails {
    border-top: 1px solid #D8E2DE;
}
#ruleColumn {
    background: #FAFCFB;
    border: 1px solid #DDE7E3;
    border-radius: 9px;
}
#ruleCaption {
    color: #168063;
    font-size: 8px;
    font-weight: 800;
    letter-spacing: 0.8px;
}
#ruleText {
    color: #536B71;
    font-size: 10px;
}
#checkBadge, #successBadge {
    color: #117658;
    background: #DDF4EB;
    border-radius: 14px;
    font-weight: 800;
}
#successBadge { border-radius: 21px; font-size: 17px; }
#requirementText { color: #5C7277; font-size: 11px; }
#fileCard {
    background: #FFFFFF;
    border: 1px solid #CFE1DB;
    border-radius: 14px;
}
#fileName { color: #17343D; font-size: 14px; font-weight: 700; }
#errorBanner {
    color: #9B3B38;
    background: #FDECEA;
    border: 1px solid #F3C8C4;
    border-radius: 10px;
    padding: 13px 16px;
}
#backButton {
    color: #294750;
    background: #F1F4F3;
    border: none;
    border-radius: 17px;
    font-size: 25px;
    font-weight: 400;
    width: 34px;
    height: 34px;
}
#backButton:hover { background: #E4EFEB; color: #14785E; }
#editorTitle {
    color: #112C36;
    font-size: 25px;
    font-weight: 700;
    letter-spacing: -0.5px;
}
#searchInput {
    min-height: 38px;
    padding: 0 12px;
    background: #FFFFFF;
    border: 1px solid #CAD7D4;
    border-radius: 9px;
    color: #17343D;
    selection-background-color: #BCEBDB;
}
#searchInput:focus { border: 1px solid #20B88A; }
#filterCheck { spacing: 8px; color: #526A70; font-size: 12px; }
#filterCheck::indicator {
    width: 17px; height: 17px;
    border: 1px solid #A8BAB6;
    border-radius: 5px;
    background: white;
}
#filterCheck::indicator:checked { background: #20B88A; border-color: #20B88A; }
#overviewBar {
    background: #E8EFEC;
    border: 1px solid #D7E2DE;
    border-radius: 10px;
}
#overviewStrong {
    color: #173E48;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1px;
}
#overviewText { color: #62787D; font-size: 11px; }
#overviewDivider { color: #CAD7D3; }
#modifiedCount {
    color: #77898D;
    background: #DDE5E2;
    border-radius: 8px;
    padding: 5px 9px;
    font-size: 9px;
    font-weight: 800;
    letter-spacing: 1px;
}
#modifiedCount[active="true"] { color: #117658; background: #CDEEE2; }
#registerScroll { background: transparent; }
#registerScroll > QWidget > QWidget { background: transparent; }
#moduleScroll { background: transparent; }
#moduleScroll > QWidget > QWidget { background: transparent; }
#moduleCard {
    background: #FFFFFF;
    border: 1px solid #D9E4E0;
    border-radius: 14px;
}
#moduleCard:hover {
    background: #FBFFFD;
    border: 1px solid #65C9AA;
}
#moduleCard:focus { border: 2px solid #20B88A; }
#moduleCard[modified="true"] {
    background: #F8FFFC;
    border: 1px solid #38BB93;
}
#moduleCard[modified="true"] #moduleEditCount {
    color: #117658;
    background: #DDF4EB;
}
#moduleType {
    color: #20A781;
    font-size: 8px;
    font-weight: 800;
    letter-spacing: 1.1px;
}
#moduleName {
    color: #15363F;
    font-size: 13px;
    font-weight: 750;
}
#moduleAddress {
    color: #6B8085;
    font-size: 9px;
    font-family: "SF Mono", "Consolas", monospace;
}
#moduleEditCount {
    color: #708589;
    background: #EEF3F1;
    border-radius: 7px;
    padding: 3px 7px;
    font-size: 8px;
    font-weight: 750;
    letter-spacing: 0.7px;
}
#changeLogPanel {
    background: #FFFFFF;
    border: 1px solid #D9E4E0;
    border-radius: 13px;
}
#logTitle {
    color: #173E48;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.2px;
}
#logCount { color: #849599; font-size: 9px; }
#logClearButton {
    min-height: 25px;
    padding: 0 7px;
    background: transparent;
    border: none;
    color: #168063;
    font-size: 10px;
}
#logClearButton:hover { background: #E8F6F1; }
#logEmpty {
    color: #94A3A6;
    background: #F5F7F6;
    border: 1px dashed #CBD7D3;
    border-radius: 9px;
    padding: 22px 15px;
    font-size: 10px;
}
#logEntries {
    background: transparent;
    border: none;
    outline: none;
    color: #445D63;
    font-size: 10px;
}
#logEntries::item {
    background: #F5F8F7;
    border: 1px solid #E3EAE8;
    border-radius: 8px;
    padding: 7px 9px;
}
#logEntries::item:selected {
    background: #E5F5EF;
    color: #245247;
}
QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background: #B9C7C3;
    min-height: 36px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover { background: #8FA6A0; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
#registerRow {
    background: #FFFFFF;
    border: 1px solid #DDE5E2;
    border-radius: 13px;
}
#registerRow:hover { border-color: #B6CAC4; }
#registerRow[modified="true"] {
    background: #FCFFFD;
    border: 1px solid #71CEB1;
}
#addressBadge {
    color: #196D58;
    background: #E5F5EF;
    border-radius: 7px;
    padding: 4px 8px;
    font-size: 11px;
    font-weight: 750;
    font-family: "SF Mono", "Consolas", monospace;
}
#registerName {
    color: #17343D;
    font-size: 14px;
    font-weight: 700;
}
#bitNumber {
    color: #839499;
    font-size: 9px;
    font-weight: 700;
}
#reservedField {
    color: #A5B1B2;
    background: #F1F3F2;
    border-radius: 6px;
    font-size: 9px;
    font-style: italic;
}
#fieldSummary {
    color: #4E666C;
    font-size: 10px;
}
#currentValue {
    color: #143943;
    font-size: 20px;
    font-weight: 750;
    font-family: "SF Mono", "Consolas", monospace;
}
#changedPill {
    color: #117658;
    background: #DDF4EB;
    border-radius: 7px;
    padding: 3px 7px;
    font-size: 8px;
    font-weight: 800;
    letter-spacing: 1px;
}
#fieldDetailsPanel {
    background: #FFFFFF;
    border: 1px solid #D8E4E0;
    border-radius: 14px;
}
#fieldDetailsEyebrow, #fieldDetailsCaption {
    color: #168063;
    font-size: 9px;
    font-weight: 800;
    letter-spacing: 1.25px;
}
#fieldDetailsTitle {
    color: #17343D;
    font-size: 18px;
    font-weight: 720;
}
#descriptionMatchBadge {
    color: #76898D;
    background: #EDF1F0;
    border-radius: 8px;
    padding: 5px 9px;
    font-size: 8px;
    font-weight: 800;
    letter-spacing: 0.9px;
}
#descriptionMatchBadge[selected="true"] {
    color: #91622D;
    background: #FFF0DA;
}
#descriptionMatchBadge[matched="true"] {
    color: #117658;
    background: #DDF4EB;
}
#fieldDetailsNameInput {
    min-height: 37px;
    padding: 0 11px;
    background: #F8FAF9;
    border: 1px solid #CAD8D4;
    border-radius: 8px;
    color: #17343D;
    font-size: 12px;
    font-weight: 650;
    selection-background-color: #BCEBDB;
}
#fieldDetailsNameInput:focus {
    background: #FFFFFF;
    border: 1px solid #20B88A;
}
#fieldDetailsNameInput:disabled {
    color: #9AA9AB;
    background: #F1F3F2;
}
#fieldDetailsApply {
    min-height: 37px;
    padding: 0 13px;
    color: #FFFFFF;
    background: #173E48;
    border: 1px solid #173E48;
}
#fieldDetailsApply:hover { background: #0F3038; }
#fieldDetailsApply:disabled {
    color: #A6B2B3;
    background: #EDF0EF;
    border-color: #DCE3E1;
}
#descriptionApply {
    min-height: 29px;
    padding: 0 11px;
    color: #14785E;
    background: #E4F6EF;
    border: 1px solid #BEE4D7;
    border-radius: 7px;
    font-size: 10px;
}
#descriptionApply:hover {
    color: #FFFFFF;
    background: #168063;
    border-color: #168063;
}
#descriptionApply:disabled {
    color: #A0ADAF;
    background: #EEF1F0;
    border-color: #DFE5E3;
}
#fieldDetailsMetadata {
    color: #315E64;
    font-size: 10px;
    font-weight: 700;
    font-family: "SF Mono", "Consolas", monospace;
}
#fieldDetailsSource {
    color: #829397;
    font-size: 10px;
}
#fieldDetailsDivider { color: #E1E8E5; }
#fieldDescriptionText {
    color: #405B62;
    background: #F6F9F7;
    border: 1px solid #E3EBE8;
    border-radius: 9px;
    padding: 12px 14px;
    font-size: 11px;
    selection-background-color: #BCEBDB;
}
#fieldDescriptionText:focus {
    background: #FFFFFF;
    border: 1px solid #20B88A;
}
#fieldDescriptionText:disabled {
    color: #849397;
    background: #F1F4F2;
    border-color: #E0E6E4;
}
QMessageBox { background: #F8FAF8; }
"""
