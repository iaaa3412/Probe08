VERSION 5.00
Begin VB.Form frmOpening
  Caption = "Opening Form"
  ScaleMode = 1
  AutoRedraw = False
  FontTransparent = True
  Icon = "frmOpening.frx":0000
  LinkTopic = "Form1"
  ClientLeft = 165
  ClientTop = 735
  ClientWidth = 8730
  ClientHeight = 5895
  StartUpPosition = 3 'Windows Default
  Begin VB.CheckBox chkSuppressDebug
    Caption = "Suppress Debug Messages"
    Left = 240
    Top = 3840
    Width = 2775
    Height = 255
    TabIndex = 17
  End
  Begin VB.Timer Timer1
    Left = 2520
    Top = 2760
  End
  Begin VB.ComboBox comboRecipes
    Left = 3240
    Top = 4920
    Width = 5175
    Height = 315
    TabIndex = 7
  End
  Begin VB.TextBox txtWaferID
    Left = 4680
    Top = 3960
    Width = 3015
    Height = 285
    Text = "The Wafer ID"
    TabIndex = 5
  End
  Begin VB.TextBox txtProcessStep
    Left = 4680
    Top = 4440
    Width = 3015
    Height = 285
    Text = "The Process Step"
    TabIndex = 6
    Tag = "View=Full;"
  End
  Begin VB.TextBox txtOperatorID
    Left = 4680
    Top = 3480
    Width = 3015
    Height = 285
    Text = "Operator Name"
    TabIndex = 4
    Tag = "View=Full;"
  End
  Begin VB.Frame Frame1
    Caption = "Operational Mode"
    Left = 3840
    Top = 720
    Width = 4335
    Height = 1695
    TabIndex = 1
    BeginProperty Font
      Name = "MS Sans Serif"
      Size = 8.25
      Charset = 0
      Weight = 700
      Underline = 0 'False
      Italic = 0 'False
      Strikethrough = 0 'False
    EndProperty
    Begin VB.OptionButton Option2
      Caption = "Engineering Mode with display and quick data logging only"
      Left = 240
      Top = 840
      Width = 3735
      Height = 615
      TabIndex = 3
    End
    Begin VB.OptionButton Option1
      Caption = "Run a full production probe with data collection"
      Left = 240
      Top = 360
      Width = 3855
      Height = 375
      TabIndex = 2
    End
  End
  Begin VB.CommandButton cmdGo
    Caption = "GO"
    Left = 360
    Top = 2760
    Width = 1215
    Height = 495
    TabIndex = 9
  End
  Begin VB.Label lblHotWire
    Caption = "NOT FOR PRODUCTION: This is a hot wired debug version only"
    Left = 3720
    Top = 2520
    Width = 4695
    Height = 735
    TabIndex = 19
    BeginProperty Font
      Name = "MS Sans Serif"
      Size = 13.5
      Charset = 0
      Weight = 400
      Underline = 0 'False
      Italic = 0 'False
      Strikethrough = 0 'False
    EndProperty
  End
  Begin VB.Label lblVersion
    Caption = "Version Number"
    Left = 3960
    Top = 120
    Width = 4215
    Height = 255
    TabIndex = 18
    Alignment = 1 'Right Justify
  End
  Begin VB.Label lblInfo
    Left = 240
    Top = 5400
    Width = 8415
    Height = 375
    TabIndex = 16
  End
  Begin VB.Label Label8
    Caption = "Recipes Available"
    Left = 840
    Top = 4920
    Width = 2055
    Height = 255
    TabIndex = 15
    Alignment = 1 'Right Justify
    Tag = "View=Full;"
  End
  Begin VB.Label Label7
    Caption = "Make sure the prober is Online (yellow On Line Key) - display says 'X I/O...ONLINE'"
    Left = 120
    Top = 1320
    Width = 3735
    Height = 495
    TabIndex = 14
    BeginProperty Font
      Name = "MS Sans Serif"
      Size = 8.25
      Charset = 0
      Weight = 700
      Underline = 0 'False
      Italic = 0 'False
      Strikethrough = 0 'False
    EndProperty
  End
  Begin VB.Label Label6
    Caption = "Click the GO button below"
    Left = 120
    Top = 1920
    Width = 3375
    Height = 375
    TabIndex = 13
    BeginProperty Font
      Name = "MS Sans Serif"
      Size = 8.25
      Charset = 0
      Weight = 700
      Underline = 0 'False
      Italic = 0 'False
      Strikethrough = 0 'False
    EndProperty
  End
  Begin VB.Label Label5
    Caption = "Load the wafer and conduct the pre-alignment"
    Left = 120
    Top = 720
    Width = 3375
    Height = 495
    TabIndex = 12
    BeginProperty Font
      Name = "MS Sans Serif"
      Size = 8.25
      Charset = 0
      Weight = 700
      Underline = 0 'False
      Italic = 0 'False
      Strikethrough = 0 'False
    EndProperty
  End
  Begin VB.Label Label4
    Caption = "Wafer ID"
    Left = 3360
    Top = 3960
    Width = 1215
    Height = 255
    TabIndex = 11
    Alignment = 1 'Right Justify
    Tag = "View=Full;"
  End
  Begin VB.Label Label3
    Caption = "Process Step"
    Left = 3360
    Top = 4440
    Width = 1215
    Height = 255
    TabIndex = 10
    Alignment = 1 'Right Justify
    Tag = "View=Full;"
  End
  Begin VB.Label Label2
    Caption = "Operator ID"
    Left = 3360
    Top = 3480
    Width = 1215
    Height = 255
    TabIndex = 8
    Alignment = 1 'Right Justify
    Tag = "View=Full;"
  End
  Begin VB.Label Label1
    Caption = "LampElectrical Probing"
    Left = 480
    Top = 120
    Width = 3135
    Height = 495
    TabIndex = 0
    BeginProperty Font
      Name = "MS Sans Serif"
      Size = 12
      Charset = 0
      Weight = 700
      Underline = 0 'False
      Italic = 0 'False
      Strikethrough = 0 'False
    EndProperty
  End
  Begin VB.Menu File
    Caption = "File"
    Begin VB.Menu SetProberName
      Index = 0
      Caption = "Set Prober Name"
    End
    Begin VB.Menu ProberExit
      Index = 1
      Caption = "Exit"
    End
  End
End

Attribute VB_Name = "frmOpening"



Private Sub Option2_Click() '40C400
  loc_0040C400: push ebp
  loc_0040C401: mov ebp, esp
  loc_0040C403: sub esp, 0000000Ch
  loc_0040C406: push 00401AA6h ; __vbaExceptHandler
  loc_0040C40B: mov eax, fs:[00000000h]
  loc_0040C411: push eax
  loc_0040C412: mov fs:[00000000h], esp
  loc_0040C419: sub esp, 0000000Ch
  loc_0040C41C: push ebx
  loc_0040C41D: push esi
  loc_0040C41E: push edi
  loc_0040C41F: mov var_C, esp
  loc_0040C422: mov var_8, 00401248h
  loc_0040C429: mov esi, Me
  loc_0040C42C: mov eax, esi
  loc_0040C42E: and eax, 00000001h
  loc_0040C431: mov var_4, eax
  loc_0040C434: and esi, FFFFFFFEh
  loc_0040C437: push esi
  loc_0040C438: mov Me, esi
  loc_0040C43B: mov ecx, [esi]
  loc_0040C43D: call [ecx+00000004h]
  loc_0040C440: mov edx, [esi]
  loc_0040C442: lea eax, var_18
  loc_0040C445: xor edi, edi
  loc_0040C447: push eax
  loc_0040C448: mov var_18, edi
  loc_0040C44B: push esi
  loc_0040C44C: mov var_18, 00000002h
  loc_0040C453: call [edx+00000708h]
  loc_0040C459: mov var_4, edi
  loc_0040C45C: mov eax, Me
  loc_0040C45F: push eax
  loc_0040C460: mov ecx, [eax]
  loc_0040C462: call [ecx+00000008h]
  loc_0040C465: mov eax, var_4
  loc_0040C468: mov ecx, var_14
  loc_0040C46B: pop edi
  loc_0040C46C: pop esi
  loc_0040C46D: mov fs:[00000000h], ecx
  loc_0040C474: pop ebx
  loc_0040C475: mov esp, ebp
  loc_0040C477: pop ebp
  loc_0040C478: retn 0004h
End Sub

Private Sub ProberExit_Click() '40C4B0
  loc_0040C4B0: push ebp
  loc_0040C4B1: mov ebp, esp
  loc_0040C4B3: sub esp, 0000000Ch
  loc_0040C4B6: push 00401AA6h ; __vbaExceptHandler
  loc_0040C4BB: mov eax, fs:[00000000h]
  loc_0040C4C1: push eax
  loc_0040C4C2: mov fs:[00000000h], esp
  loc_0040C4C9: sub esp, 00000008h
  loc_0040C4CC: push ebx
  loc_0040C4CD: push esi
  loc_0040C4CE: push edi
  loc_0040C4CF: mov var_C, esp
  loc_0040C4D2: mov var_8, 00401250h
  loc_0040C4D9: mov eax, Me
  loc_0040C4DC: mov ecx, eax
  loc_0040C4DE: and ecx, 00000001h
  loc_0040C4E1: mov var_4, ecx
  loc_0040C4E4: and al, FEh
  loc_0040C4E6: push eax
  loc_0040C4E7: mov Me, eax
  loc_0040C4EA: mov edx, [eax]
  loc_0040C4EC: call [edx+00000004h]
  loc_0040C4EF: call 0041ECE0h
  loc_0040C4F4: mov var_4, 00000000h
  loc_0040C4FB: mov eax, Me
  loc_0040C4FE: push eax
  loc_0040C4FF: mov ecx, [eax]
  loc_0040C501: call [ecx+00000008h]
  loc_0040C504: mov eax, var_4
  loc_0040C507: mov ecx, var_14
  loc_0040C50A: pop edi
  loc_0040C50B: pop esi
  loc_0040C50C: mov fs:[00000000h], ecx
  loc_0040C513: pop ebx
  loc_0040C514: mov esp, ebp
  loc_0040C516: pop ebp
  loc_0040C517: retn 0008h
End Sub

Private Sub SetProberName_Click() '40C520
  loc_0040C520: push ebp
  loc_0040C521: mov ebp, esp
  loc_0040C523: sub esp, 0000000Ch
  loc_0040C526: push 00401AA6h ; __vbaExceptHandler
  loc_0040C52B: mov eax, fs:[00000000h]
  loc_0040C531: push eax
  loc_0040C532: mov fs:[00000000h], esp
  loc_0040C539: sub esp, 000000E0h
  loc_0040C53F: push ebx
  loc_0040C540: push esi
  loc_0040C541: push edi
  loc_0040C542: mov var_C, esp
  loc_0040C545: mov var_8, 00401258h
  loc_0040C54C: mov eax, Me
  loc_0040C54F: mov ecx, eax
  loc_0040C551: and ecx, 00000001h
  loc_0040C554: mov var_4, ecx
  loc_0040C557: and al, FEh
  loc_0040C559: push eax
  loc_0040C55A: mov Me, eax
  loc_0040C55D: mov edx, [eax]
  loc_0040C55F: call [edx+00000004h]
  loc_0040C562: sub esp, 00000010h
  loc_0040C565: xor esi, esi
  loc_0040C567: mov edx, esp
  loc_0040C569: mov ecx, 00000008h
  loc_0040C56E: mov var_8C, esi
  loc_0040C574: mov var_8C, ecx
  loc_0040C57A: mov [edx], ecx
  loc_0040C57C: mov ecx, var_88
  loc_0040C582: mov eax, 00405CA4h ; "IMTPRB02"
  loc_0040C587: push 00405C88h ; "ProberName"
  loc_0040C58C: mov [edx+00000004h], ecx
  loc_0040C58F: mov var_84, eax
  loc_0040C595: push 00405C78h ; "Names"
  loc_0040C59A: push 00405C60h ; "IMTProber"
  loc_0040C59F: mov [edx+00000008h], eax
  loc_0040C5A2: mov eax, var_80
  loc_0040C5A5: mov var_18, esi
  loc_0040C5A8: mov var_1C, esi
  loc_0040C5AB: mov var_2C, esi
  loc_0040C5AE: mov var_3C, esi
  loc_0040C5B1: mov var_4C, esi
  loc_0040C5B4: mov var_5C, esi
  loc_0040C5B7: mov var_6C, esi
  loc_0040C5BA: mov var_7C, esi
  loc_0040C5BD: mov var_9C, esi
  loc_0040C5C3: mov var_AC, esi
  loc_0040C5C9: mov [edx+0000000Ch], eax
  loc_0040C5CC: call [004011A0h] ; rtcGetSetting
  loc_0040C5D2: mov edi, [004011D0h] ; __vbaStrMove
  loc_0040C5D8: mov edx, eax
  loc_0040C5DA: lea ecx, var_18
  loc_0040C5DD: call edi
  loc_0040C5DF: mov ecx, 80020004h
  loc_0040C5E4: mov ebx, [004011B4h] ; __vbaVarDup
  loc_0040C5EA: mov var_74, ecx
  loc_0040C5ED: mov var_64, ecx
  loc_0040C5F0: mov ecx, 00000FA0h
  loc_0040C5F5: mov eax, 0000000Ah
  loc_0040C5FA: mov var_54, ecx
  loc_0040C5FD: mov var_44, ecx
  loc_0040C600: lea ecx, var_18
  loc_0040C603: mov var_7C, eax
  loc_0040C606: mov var_6C, eax
  loc_0040C609: mov eax, 00000002h
  loc_0040C60E: mov var_A4, ecx
  loc_0040C614: lea edx, var_9C
  loc_0040C61A: lea ecx, var_3C
  loc_0040C61D: mov var_5C, eax
  loc_0040C620: mov var_4C, eax
  loc_0040C623: mov var_AC, 00004008h
  loc_0040C62D: mov var_94, 00405D5Ch ; "Prober Name"
  loc_0040C637: mov var_9C, 00000008h
  loc_0040C641: call ebx
  loc_0040C643: lea edx, var_8C
  loc_0040C649: lea ecx, var_2C
  loc_0040C64C: mov var_84, 00405CBCh ; "Enter a new name for this prober so as to identify its data in the database."
  loc_0040C656: mov var_8C, 00000008h
  loc_0040C660: call ebx
  loc_0040C662: lea edx, var_7C
  loc_0040C665: lea eax, var_6C
  loc_0040C668: push edx
  loc_0040C669: lea ecx, var_5C
  loc_0040C66C: push eax
  loc_0040C66D: lea edx, var_4C
  loc_0040C670: push ecx
  loc_0040C671: push edx
  loc_0040C672: lea eax, var_AC
  loc_0040C678: lea ecx, var_3C
  loc_0040C67B: push eax
  loc_0040C67C: lea edx, var_2C
  loc_0040C67F: push ecx
  loc_0040C680: push edx
  loc_0040C681: call [00401088h] ; rtcInputBox
  loc_0040C687: mov edx, eax
  loc_0040C689: lea ecx, var_18
  loc_0040C68C: call edi
  loc_0040C68E: lea eax, var_7C
  loc_0040C691: lea ecx, var_6C
  loc_0040C694: push eax
  loc_0040C695: lea edx, var_5C
  loc_0040C698: push ecx
  loc_0040C699: lea eax, var_4C
  loc_0040C69C: push edx
  loc_0040C69D: lea ecx, var_3C
  loc_0040C6A0: push eax
  loc_0040C6A1: lea edx, var_2C
  loc_0040C6A4: push ecx
  loc_0040C6A5: push edx
  loc_0040C6A6: push 00000006h
  loc_0040C6A8: call [00401038h] ; __vbaFreeVarList
  loc_0040C6AE: mov eax, var_18
  loc_0040C6B1: add esp, 0000001Ch
  loc_0040C6B4: push eax
  loc_0040C6B5: push esi
  loc_0040C6B6: call [004010DCh] ; __vbaStrCmp
  loc_0040C6BC: test eax, eax
  loc_0040C6BE: jz 0040C777h
  loc_0040C6C4: mov ecx, var_18
  loc_0040C6C7: push ecx
  loc_0040C6C8: push 00405C88h ; "ProberName"
  loc_0040C6CD: push 00405C78h ; "Names"
  loc_0040C6D2: push 00405C60h ; "IMTProber"
  loc_0040C6D7: call [00401008h] ; rtcSaveSetting
  loc_0040C6DD: mov ecx, 0000000Ah
  loc_0040C6E2: mov eax, 80020004h
  loc_0040C6E7: mov var_5C, ecx
  loc_0040C6EA: mov var_4C, ecx
  loc_0040C6ED: lea edx, var_8C
  loc_0040C6F3: lea ecx, var_3C
  loc_0040C6F6: mov var_54, eax
  loc_0040C6F9: mov var_44, eax
  loc_0040C6FC: mov var_84, 004050E8h ; "IMT LampElectrical Probing"
  loc_0040C706: mov var_8C, 00000008h
  loc_0040C710: call ebx
  loc_0040C712: mov edx, var_18
  loc_0040C715: mov ebx, [00401050h] ; __vbaStrCat
  loc_0040C71B: push 00405D78h ; "Prober Name '"
  loc_0040C720: push edx
  loc_0040C721: call ebx
  loc_0040C723: mov edx, eax
  loc_0040C725: lea ecx, var_1C
  loc_0040C728: call edi
  loc_0040C72A: push eax
  loc_0040C72B: push 00405D98h ; "' saved."
  loc_0040C730: call ebx
  loc_0040C732: mov var_24, eax
  loc_0040C735: lea eax, var_5C
  loc_0040C738: lea ecx, var_4C
  loc_0040C73B: push eax
  loc_0040C73C: lea edx, var_3C
  loc_0040C73F: push ecx
  loc_0040C740: push edx
  loc_0040C741: lea eax, var_2C
  loc_0040C744: push esi
  loc_0040C745: push eax
  loc_0040C746: mov var_2C, 00000008h
  loc_0040C74D: call [00401084h] ; rtcMsgBox
  loc_0040C753: lea ecx, var_1C
  loc_0040C756: call [004011F4h] ; __vbaFreeStr
  loc_0040C75C: lea ecx, var_5C
  loc_0040C75F: lea edx, var_4C
  loc_0040C762: push ecx
  loc_0040C763: lea eax, var_3C
  loc_0040C766: push edx
  loc_0040C767: lea ecx, var_2C
  loc_0040C76A: push eax
  loc_0040C76B: push ecx
  loc_0040C76C: push 00000004h
  loc_0040C76E: call [00401038h] ; __vbaFreeVarList
  loc_0040C774: add esp, 00000014h
  loc_0040C777: mov var_4, esi
  loc_0040C77A: push 0040C7B8h
  loc_0040C77F: jmp 0040C7AEh
  loc_0040C781: lea ecx, var_1C
  loc_0040C784: call [004011F4h] ; __vbaFreeStr
  loc_0040C78A: lea edx, var_7C
  loc_0040C78D: lea eax, var_6C
  loc_0040C790: push edx
  loc_0040C791: lea ecx, var_5C
  loc_0040C794: push eax
  loc_0040C795: lea edx, var_4C
  loc_0040C798: push ecx
  loc_0040C799: lea eax, var_3C
  loc_0040C79C: push edx
  loc_0040C79D: lea ecx, var_2C
  loc_0040C7A0: push eax
  loc_0040C7A1: push ecx
  loc_0040C7A2: push 00000006h
  loc_0040C7A4: call [00401038h] ; __vbaFreeVarList
  loc_0040C7AA: add esp, 0000001Ch
  loc_0040C7AD: ret
  loc_0040C7AE: lea ecx, var_18
  loc_0040C7B1: call [004011F4h] ; __vbaFreeStr
  loc_0040C7B7: ret
  loc_0040C7B8: mov eax, Me
  loc_0040C7BB: push eax
  loc_0040C7BC: mov edx, [eax]
  loc_0040C7BE: call [edx+00000008h]
  loc_0040C7C1: mov eax, var_4
  loc_0040C7C4: mov ecx, var_14
  loc_0040C7C7: pop edi
  loc_0040C7C8: pop esi
  loc_0040C7C9: mov fs:[00000000h], ecx
  loc_0040C7D0: pop ebx
  loc_0040C7D1: mov esp, ebp
  loc_0040C7D3: pop ebp
  loc_0040C7D4: retn 0008h
End Sub

Private Sub cmdGo_Click() '40AE20
  loc_0040AE20: push ebp
  loc_0040AE21: mov ebp, esp
  loc_0040AE23: sub esp, 0000000Ch
  loc_0040AE26: push 00401AA6h ; __vbaExceptHandler
  loc_0040AE2B: mov eax, fs:[00000000h]
  loc_0040AE31: push eax
  loc_0040AE32: mov fs:[00000000h], esp
  loc_0040AE39: sub esp, 000000C0h
  loc_0040AE3F: push ebx
  loc_0040AE40: push esi
  loc_0040AE41: push edi
  loc_0040AE42: mov var_C, esp
  loc_0040AE45: mov var_8, 00401210h
  loc_0040AE4C: mov esi, Me
  loc_0040AE4F: mov eax, esi
  loc_0040AE51: and eax, 00000001h
  loc_0040AE54: mov var_4, eax
  loc_0040AE57: and esi, FFFFFFFEh
  loc_0040AE5A: push esi
  loc_0040AE5B: mov Me, esi
  loc_0040AE5E: mov ecx, [esi]
  loc_0040AE60: call [ecx+00000004h]
  loc_0040AE63: mov edx, [esi]
  loc_0040AE65: xor ebx, ebx
  loc_0040AE67: push esi
  loc_0040AE68: mov var_18, ebx
  loc_0040AE6B: mov var_1C, ebx
  loc_0040AE6E: mov var_20, ebx
  loc_0040AE71: mov var_24, ebx
  loc_0040AE74: mov var_28, ebx
  loc_0040AE77: mov var_2C, ebx
  loc_0040AE7A: mov var_3C, ebx
  loc_0040AE7D: mov var_4C, ebx
  loc_0040AE80: mov var_5C, ebx
  loc_0040AE83: mov var_6C, ebx
  loc_0040AE86: mov var_7C, ebx
  loc_0040AE89: mov var_8C, ebx
  loc_0040AE8F: mov var_B0, ebx
  loc_0040AE95: call [edx+0000031Ch]
  loc_0040AE9B: push eax
  loc_0040AE9C: lea eax, var_2C
  loc_0040AE9F: push eax
  loc_0040AEA0: call [00401080h] ; __vbaObjSet
  loc_0040AEA6: mov edi, eax
  loc_0040AEA8: lea edx, var_B0
  loc_0040AEAE: push edx
  loc_0040AEAF: push edi
  loc_0040AEB0: mov ecx, [edi]
  loc_0040AEB2: call [ecx+000000E0h]
  loc_0040AEB8: cmp eax, ebx
  loc_0040AEBA: fnclex
  loc_0040AEBC: jge 0040AED0h
  loc_0040AEBE: push 000000E0h
  loc_0040AEC3: push 00405388h
  loc_0040AEC8: push edi
  loc_0040AEC9: push eax
  loc_0040AECA: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040AED0: xor eax, eax
  loc_0040AED2: cmp var_B0, FFFFFFh
  loc_0040AEDA: lea ecx, var_2C
  loc_0040AEDD: setz al
  loc_0040AEE0: neg eax
  loc_0040AEE2: mov edi, eax
  loc_0040AEE4: call [004011F0h] ; __vbaFreeObj
  loc_0040AEEA: neg di
  loc_0040AEED: sbb edi, edi
  loc_0040AEEF: push esi
  loc_0040AEF0: mov [00423032h], di
  loc_0040AEF7: mov ecx, [esi]
  loc_0040AEF9: call [ecx+00000308h]
  loc_0040AEFF: lea edx, var_2C
  loc_0040AF02: push eax
  loc_0040AF03: push edx
  loc_0040AF04: call [00401080h] ; __vbaObjSet
  loc_0040AF0A: mov edi, eax
  loc_0040AF0C: lea ecx, var_20
  loc_0040AF0F: push ecx
  loc_0040AF10: push edi
  loc_0040AF11: mov eax, [edi]
  loc_0040AF13: call [eax+000000A0h]
  loc_0040AF19: cmp eax, ebx
  loc_0040AF1B: fnclex
  loc_0040AF1D: jge 0040AF31h
  loc_0040AF1F: push 000000A0h
  loc_0040AF24: push 00405398h
  loc_0040AF29: push edi
  loc_0040AF2A: push eax
  loc_0040AF2B: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040AF31: mov eax, var_20
  loc_0040AF34: lea edx, var_3C
  loc_0040AF37: mov var_34, eax
  loc_0040AF3A: lea eax, var_4C
  loc_0040AF3D: push edx
  loc_0040AF3E: push eax
  loc_0040AF3F: mov var_20, ebx
  loc_0040AF42: mov var_3C, 00000008h
  loc_0040AF49: call [004010A4h] ; rtcTrimVar
  loc_0040AF4F: lea ecx, var_4C
  loc_0040AF52: push ecx
  loc_0040AF53: call [00401030h] ; __vbaStrVarMove
  loc_0040AF59: mov edx, eax
  loc_0040AF5B: lea ecx, var_18
  loc_0040AF5E: call [004011D0h] ; __vbaStrMove
  loc_0040AF64: lea ecx, var_2C
  loc_0040AF67: call [004011F0h] ; __vbaFreeObj
  loc_0040AF6D: lea edx, var_4C
  loc_0040AF70: lea eax, var_3C
  loc_0040AF73: push edx
  loc_0040AF74: push eax
  loc_0040AF75: push 00000002h
  loc_0040AF77: call [00401038h] ; __vbaFreeVarList
  loc_0040AF7D: mov ecx, var_18
  loc_0040AF80: mov edi, [004010DCh] ; __vbaStrCmp
  loc_0040AF86: add esp, 0000000Ch
  loc_0040AF89: push ecx
  loc_0040AF8A: push 004053ACh ; "The Wafer ID"
  loc_0040AF8F: call edi
  loc_0040AF91: mov edx, eax
  loc_0040AF93: mov eax, var_18
  loc_0040AF96: neg edx
  loc_0040AF98: sbb edx, edx
  loc_0040AF9A: push eax
  loc_0040AF9B: neg edx
  loc_0040AF9D: push ebx
  loc_0040AF9E: mov var_D4, edx
  loc_0040AFA4: call edi
  loc_0040AFA6: mov ecx, var_D4
  loc_0040AFAC: neg eax
  loc_0040AFAE: sbb eax, eax
  loc_0040AFB0: neg eax
  loc_0040AFB2: test eax, ecx
  loc_0040AFB4: jnz 0040B040h
  loc_0040AFBA: mov esi, [004011B4h] ; __vbaVarDup
  loc_0040AFC0: mov ecx, 80020004h
  loc_0040AFC5: mov var_64, ecx
  loc_0040AFC8: mov eax, 0000000Ah
  loc_0040AFCD: mov var_54, ecx
  loc_0040AFD0: mov edi, 00000008h
  loc_0040AFD5: lea edx, var_8C
  loc_0040AFDB: lea ecx, var_4C
  loc_0040AFDE: mov var_6C, eax
  loc_0040AFE1: mov var_5C, eax
  loc_0040AFE4: mov var_84, 004050E8h ; "IMT LampElectrical Probing"
  loc_0040AFEE: mov var_8C, edi
  loc_0040AFF4: call __vbaVarDup
  loc_0040AFF6: lea edx, var_7C
  loc_0040AFF9: lea ecx, var_3C
  loc_0040AFFC: mov var_74, 004053CCh ; "Please enter the Wafer ID."
  loc_0040B003: mov var_7C, edi
  loc_0040B006: call __vbaVarDup
  loc_0040B008: lea edx, var_6C
  loc_0040B00B: lea eax, var_5C
  loc_0040B00E: push edx
  loc_0040B00F: lea ecx, var_4C
  loc_0040B012: push eax
  loc_0040B013: push ecx
  loc_0040B014: lea edx, var_3C
  loc_0040B017: push 00000030h
  loc_0040B019: push edx
  loc_0040B01A: call [00401084h] ; rtcMsgBox
  loc_0040B020: lea eax, var_6C
  loc_0040B023: lea ecx, var_5C
  loc_0040B026: push eax
  loc_0040B027: lea edx, var_4C
  loc_0040B02A: push ecx
  loc_0040B02B: lea eax, var_3C
  loc_0040B02E: push edx
  loc_0040B02F: push eax
  loc_0040B030: push 00000004h
  loc_0040B032: call [00401038h] ; __vbaFreeVarList
  loc_0040B038: add esp, 00000014h
  loc_0040B03B: jmp 0040B5D4h
  loc_0040B040: cmp [00423032h], 0000h
  loc_0040B048: jz 0040B2D4h
  loc_0040B04E: mov ecx, [esi]
  loc_0040B050: push esi
  loc_0040B051: call [ecx+00000310h]
  loc_0040B057: lea edx, var_2C
  loc_0040B05A: push eax
  loc_0040B05B: push edx
  loc_0040B05C: call [00401080h] ; __vbaObjSet
  loc_0040B062: mov ebx, eax
  loc_0040B064: lea ecx, var_20
  loc_0040B067: push ecx
  loc_0040B068: push ebx
  loc_0040B069: mov eax, [ebx]
  loc_0040B06B: call [eax+000000A0h]
  loc_0040B071: test eax, eax
  loc_0040B073: fnclex
  loc_0040B075: jge 0040B089h
  loc_0040B077: push 000000A0h
  loc_0040B07C: push 00405398h
  loc_0040B081: push ebx
  loc_0040B082: push eax
  loc_0040B083: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040B089: mov eax, var_20
  loc_0040B08C: lea edx, var_3C
  loc_0040B08F: mov var_34, eax
  loc_0040B092: lea eax, var_4C
  loc_0040B095: push edx
  loc_0040B096: push eax
  loc_0040B097: mov var_20, 00000000h
  loc_0040B09E: mov var_3C, 00000008h
  loc_0040B0A5: call [004010A4h] ; rtcTrimVar
  loc_0040B0AB: lea ecx, var_4C
  loc_0040B0AE: push ecx
  loc_0040B0AF: call [00401030h] ; __vbaStrVarMove
  loc_0040B0B5: mov edx, eax
  loc_0040B0B7: lea ecx, var_18
  loc_0040B0BA: call [004011D0h] ; __vbaStrMove
  loc_0040B0C0: lea ecx, var_2C
  loc_0040B0C3: call [004011F0h] ; __vbaFreeObj
  loc_0040B0C9: lea edx, var_4C
  loc_0040B0CC: lea eax, var_3C
  loc_0040B0CF: push edx
  loc_0040B0D0: push eax
  loc_0040B0D1: push 00000002h
  loc_0040B0D3: call [00401038h] ; __vbaFreeVarList
  loc_0040B0D9: mov ecx, var_18
  loc_0040B0DC: add esp, 0000000Ch
  loc_0040B0DF: push ecx
  loc_0040B0E0: push 00405408h ; "Operator Name"
  loc_0040B0E5: call edi
  loc_0040B0E7: mov edx, var_18
  loc_0040B0EA: mov ebx, eax
  loc_0040B0EC: neg ebx
  loc_0040B0EE: sbb ebx, ebx
  loc_0040B0F0: push edx
  loc_0040B0F1: push 00000000h
  loc_0040B0F3: neg ebx
  loc_0040B0F5: call edi
  loc_0040B0F7: neg eax
  loc_0040B0F9: sbb eax, eax
  loc_0040B0FB: neg eax
  loc_0040B0FD: test eax, ebx
  loc_0040B0FF: jnz 0040B18Bh
  loc_0040B105: mov esi, [004011B4h] ; __vbaVarDup
  loc_0040B10B: mov ecx, 80020004h
  loc_0040B110: mov var_64, ecx
  loc_0040B113: mov eax, 0000000Ah
  loc_0040B118: mov var_54, ecx
  loc_0040B11B: mov edi, 00000008h
  loc_0040B120: lea edx, var_8C
  loc_0040B126: lea ecx, var_4C
  loc_0040B129: mov var_6C, eax
  loc_0040B12C: mov var_5C, eax
  loc_0040B12F: mov var_84, 004050E8h ; "IMT LampElectrical Probing"
  loc_0040B139: mov var_8C, edi
  loc_0040B13F: call __vbaVarDup
  loc_0040B141: lea edx, var_7C
  loc_0040B144: lea ecx, var_3C
  loc_0040B147: mov var_74, 00405428h ; "Please enter your Operator ID."
  loc_0040B14E: mov var_7C, edi
  loc_0040B151: call __vbaVarDup
  loc_0040B153: lea eax, var_6C
  loc_0040B156: lea ecx, var_5C
  loc_0040B159: push eax
  loc_0040B15A: lea edx, var_4C
  loc_0040B15D: push ecx
  loc_0040B15E: push edx
  loc_0040B15F: lea eax, var_3C
  loc_0040B162: push 00000030h
  loc_0040B164: push eax
  loc_0040B165: call [00401084h] ; rtcMsgBox
  loc_0040B16B: lea ecx, var_6C
  loc_0040B16E: lea edx, var_5C
  loc_0040B171: push ecx
  loc_0040B172: lea eax, var_4C
  loc_0040B175: push edx
  loc_0040B176: lea ecx, var_3C
  loc_0040B179: push eax
  loc_0040B17A: push ecx
  loc_0040B17B: push 00000004h
  loc_0040B17D: call [00401038h] ; __vbaFreeVarList
  loc_0040B183: add esp, 00000014h
  loc_0040B186: jmp 0040B5D4h
  loc_0040B18B: mov edx, [esi]
  loc_0040B18D: push esi
  loc_0040B18E: call [edx+0000030Ch]
  loc_0040B194: push eax
  loc_0040B195: lea eax, var_2C
  loc_0040B198: push eax
  loc_0040B199: call [00401080h] ; __vbaObjSet
  loc_0040B19F: mov ebx, eax
  loc_0040B1A1: lea edx, var_20
  loc_0040B1A4: push edx
  loc_0040B1A5: push ebx
  loc_0040B1A6: mov ecx, [ebx]
  loc_0040B1A8: call [ecx+000000A0h]
  loc_0040B1AE: test eax, eax
  loc_0040B1B0: fnclex
  loc_0040B1B2: jge 0040B1C6h
  loc_0040B1B4: push 000000A0h
  loc_0040B1B9: push 00405398h
  loc_0040B1BE: push ebx
  loc_0040B1BF: push eax
  loc_0040B1C0: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040B1C6: mov eax, var_20
  loc_0040B1C9: lea ecx, var_4C
  loc_0040B1CC: mov var_34, eax
  loc_0040B1CF: lea eax, var_3C
  loc_0040B1D2: push eax
  loc_0040B1D3: push ecx
  loc_0040B1D4: mov var_20, 00000000h
  loc_0040B1DB: mov var_3C, 00000008h
  loc_0040B1E2: call [004010A4h] ; rtcTrimVar
  loc_0040B1E8: lea edx, var_4C
  loc_0040B1EB: push edx
  loc_0040B1EC: call [00401030h] ; __vbaStrVarMove
  loc_0040B1F2: mov edx, eax
  loc_0040B1F4: lea ecx, var_18
  loc_0040B1F7: call [004011D0h] ; __vbaStrMove
  loc_0040B1FD: lea ecx, var_2C
  loc_0040B200: call [004011F0h] ; __vbaFreeObj
  loc_0040B206: lea eax, var_4C
  loc_0040B209: lea ecx, var_3C
  loc_0040B20C: push eax
  loc_0040B20D: push ecx
  loc_0040B20E: push 00000002h
  loc_0040B210: call [00401038h] ; __vbaFreeVarList
  loc_0040B216: mov edx, var_18
  loc_0040B219: add esp, 0000000Ch
  loc_0040B21C: push edx
  loc_0040B21D: push 0040546Ch ; "The Process Step"
  loc_0040B222: call edi
  loc_0040B224: mov ebx, eax
  loc_0040B226: mov eax, var_18
  loc_0040B229: neg ebx
  loc_0040B22B: sbb ebx, ebx
  loc_0040B22D: push eax
  loc_0040B22E: push 00000000h
  loc_0040B230: neg ebx
  loc_0040B232: call edi
  loc_0040B234: neg eax
  loc_0040B236: sbb eax, eax
  loc_0040B238: neg eax
  loc_0040B23A: test eax, ebx
  loc_0040B23C: jnz 0040B2C8h
  loc_0040B242: mov esi, [004011B4h] ; __vbaVarDup
  loc_0040B248: mov ecx, 80020004h
  loc_0040B24D: mov var_64, ecx
  loc_0040B250: mov eax, 0000000Ah
  loc_0040B255: mov var_54, ecx
  loc_0040B258: mov edi, 00000008h
  loc_0040B25D: lea edx, var_8C
  loc_0040B263: lea ecx, var_4C
  loc_0040B266: mov var_6C, eax
  loc_0040B269: mov var_5C, eax
  loc_0040B26C: mov var_84, 004050E8h ; "IMT LampElectrical Probing"
  loc_0040B276: mov var_8C, edi
  loc_0040B27C: call __vbaVarDup
  loc_0040B27E: lea edx, var_7C
  loc_0040B281: lea ecx, var_3C
  loc_0040B284: mov var_74, 00405494h ; "Please enter the Process Step."
  loc_0040B28B: mov var_7C, edi
  loc_0040B28E: call __vbaVarDup
  loc_0040B290: lea ecx, var_6C
  loc_0040B293: lea edx, var_5C
  loc_0040B296: push ecx
  loc_0040B297: lea eax, var_4C
  loc_0040B29A: push edx
  loc_0040B29B: push eax
  loc_0040B29C: lea ecx, var_3C
  loc_0040B29F: push 00000030h
  loc_0040B2A1: push ecx
  loc_0040B2A2: call [00401084h] ; rtcMsgBox
  loc_0040B2A8: lea edx, var_6C
  loc_0040B2AB: lea eax, var_5C
  loc_0040B2AE: push edx
  loc_0040B2AF: lea ecx, var_4C
  loc_0040B2B2: push eax
  loc_0040B2B3: lea edx, var_3C
  loc_0040B2B6: push ecx
  loc_0040B2B7: push edx
  loc_0040B2B8: push 00000004h
  loc_0040B2BA: call [00401038h] ; __vbaFreeVarList
  loc_0040B2C0: add esp, 00000014h
  loc_0040B2C3: jmp 0040B5D4h
  loc_0040B2C8: push 004054D8h ; vbCrLf
  loc_0040B2CD: push 004054E4h ; "Tell an Engineer!"
  loc_0040B2D2: jmp 0040B2DEh
  loc_0040B2D4: push 004054D8h ; vbCrLf
  loc_0040B2D9: push 00405534h ; "This file is needed, even in Engineering Mode, to establish the die moves."
  loc_0040B2DE: mov ebx, [00401050h] ; __vbaStrCat
  loc_0040B2E4: call ebx
  loc_0040B2E6: mov edx, eax
  loc_0040B2E8: lea ecx, var_1C
  loc_0040B2EB: call [004011D0h] ; __vbaStrMove
  loc_0040B2F1: mov eax, [esi]
  loc_0040B2F3: push esi
  loc_0040B2F4: call [eax+00000304h]
  loc_0040B2FA: lea ecx, var_2C
  loc_0040B2FD: push eax
  loc_0040B2FE: push ecx
  loc_0040B2FF: call [00401080h] ; __vbaObjSet
  loc_0040B305: mov edx, [eax]
  loc_0040B307: lea ecx, var_20
  loc_0040B30A: push ecx
  loc_0040B30B: push eax
  loc_0040B30C: mov var_B4, eax
  loc_0040B312: call [edx+000000A8h]
  loc_0040B318: test eax, eax
  loc_0040B31A: fnclex
  loc_0040B31C: jge 0040B336h
  loc_0040B31E: mov edx, var_B4
  loc_0040B324: push 000000A8h
  loc_0040B329: push 004055DCh
  loc_0040B32E: push edx
  loc_0040B32F: push eax
  loc_0040B330: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040B336: mov eax, var_20
  loc_0040B339: push eax
  loc_0040B33A: push 004055D0h ; "ERROR"
  loc_0040B33F: call edi
  loc_0040B341: mov edi, eax
  loc_0040B343: lea ecx, var_20
  loc_0040B346: neg edi
  loc_0040B348: sbb edi, edi
  loc_0040B34A: inc edi
  loc_0040B34B: neg edi
  loc_0040B34D: call [004011F4h] ; __vbaFreeStr
  loc_0040B353: lea ecx, var_2C
  loc_0040B356: call [004011F0h] ; __vbaFreeObj
  loc_0040B35C: test di, di
  loc_0040B35F: jz 0040B426h
  loc_0040B365: mov ecx, 80020004h
  loc_0040B36A: mov eax, 0000000Ah
  loc_0040B36F: mov var_64, ecx
  loc_0040B372: mov var_54, ecx
  loc_0040B375: mov edi, 00000008h
  loc_0040B37A: lea edx, var_7C
  loc_0040B37D: lea ecx, var_4C
  loc_0040B380: mov var_6C, eax
  loc_0040B383: mov var_5C, eax
  loc_0040B386: mov var_74, 004050E8h ; "IMT LampElectrical Probing"
  loc_0040B38D: mov var_7C, edi
  loc_0040B390: call [004011B4h] ; __vbaVarDup
  loc_0040B396: push 004055F0h ; "ERROR is not a valid recipe name!"
  loc_0040B39B: push 004054D8h ; vbCrLf
  loc_0040B3A0: call ebx
  loc_0040B3A2: mov esi, [004011D0h] ; __vbaStrMove
  loc_0040B3A8: mov edx, eax
  loc_0040B3AA: lea ecx, var_20
  loc_0040B3AD: call __vbaStrMove
  loc_0040B3AF: push eax
  loc_0040B3B0: push 00405638h ; "This is caused by the system "
  loc_0040B3B5: call ebx
  loc_0040B3B7: mov edx, eax
  loc_0040B3B9: lea ecx, var_24
  loc_0040B3BC: call __vbaStrMove
  loc_0040B3BE: push eax
  loc_0040B3BF: push 00405678h ; "not locating any .PMA files in C:\ProbeRecipe\LampElectrical"
  loc_0040B3C4: call ebx
  loc_0040B3C6: mov edx, eax
  loc_0040B3C8: lea ecx, var_28
  loc_0040B3CB: call __vbaStrMove
  loc_0040B3CD: mov ecx, var_1C
  loc_0040B3D0: push eax
  loc_0040B3D1: push ecx
  loc_0040B3D2: call ebx
  loc_0040B3D4: mov var_34, eax
  loc_0040B3D7: lea edx, var_6C
  loc_0040B3DA: lea eax, var_5C
  loc_0040B3DD: push edx
  loc_0040B3DE: lea ecx, var_4C
  loc_0040B3E1: push eax
  loc_0040B3E2: push ecx
  loc_0040B3E3: lea edx, var_3C
  loc_0040B3E6: push 00000010h
  loc_0040B3E8: push edx
  loc_0040B3E9: mov var_3C, edi
  loc_0040B3EC: call [00401084h] ; rtcMsgBox
  loc_0040B3F2: lea eax, var_28
  loc_0040B3F5: lea ecx, var_24
  loc_0040B3F8: push eax
  loc_0040B3F9: lea edx, var_20
  loc_0040B3FC: push ecx
  loc_0040B3FD: push edx
  loc_0040B3FE: push 00000003h
  loc_0040B400: call [00401180h] ; __vbaFreeStrList
  loc_0040B406: lea eax, var_6C
  loc_0040B409: lea ecx, var_5C
  loc_0040B40C: push eax
  loc_0040B40D: lea edx, var_4C
  loc_0040B410: push ecx
  loc_0040B411: lea eax, var_3C
  loc_0040B414: push edx
  loc_0040B415: push eax
  loc_0040B416: push 00000004h
  loc_0040B418: call [00401038h] ; __vbaFreeVarList
  loc_0040B41E: add esp, 00000024h
  loc_0040B421: jmp 0040B5D4h
  loc_0040B426: mov ecx, [esi]
  loc_0040B428: push esi
  loc_0040B429: call [ecx+00000300h]
  loc_0040B42F: lea edx, var_2C
  loc_0040B432: push eax
  loc_0040B433: push edx
  loc_0040B434: call [00401080h] ; __vbaObjSet
  loc_0040B43A: mov edi, eax
  loc_0040B43C: push 00000000h
  loc_0040B43E: push edi
  loc_0040B43F: mov eax, [edi]
  loc_0040B441: call [eax+0000005Ch]
  loc_0040B444: test eax, eax
  loc_0040B446: fnclex
  loc_0040B448: jge 0040B459h
  loc_0040B44A: push 0000005Ch
  loc_0040B44C: push 004056F4h
  loc_0040B451: push edi
  loc_0040B452: push eax
  loc_0040B453: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040B459: mov ebx, [004011F0h] ; __vbaFreeObj
  loc_0040B45F: lea ecx, var_2C
  loc_0040B462: call ebx
  loc_0040B464: mov ecx, [esi]
  loc_0040B466: push esi
  loc_0040B467: call [ecx+00000300h]
  loc_0040B46D: lea edx, var_2C
  loc_0040B470: push eax
  loc_0040B471: push edx
  loc_0040B472: call [00401080h] ; __vbaObjSet
  loc_0040B478: mov edi, eax
  loc_0040B47A: push 00000064h
  loc_0040B47C: push edi
  loc_0040B47D: mov eax, [edi]
  loc_0040B47F: call [eax+00000064h]
  loc_0040B482: test eax, eax
  loc_0040B484: fnclex
  loc_0040B486: jge 0040B497h
  loc_0040B488: push 00000064h
  loc_0040B48A: push 004056F4h
  loc_0040B48F: push edi
  loc_0040B490: push eax
  loc_0040B491: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040B497: lea ecx, var_2C
  loc_0040B49A: call ebx
  loc_0040B49C: mov ecx, [esi]
  loc_0040B49E: push esi
  loc_0040B49F: call [ecx+00000300h]
  loc_0040B4A5: lea edx, var_2C
  loc_0040B4A8: push eax
  loc_0040B4A9: push edx
  loc_0040B4AA: call [00401080h] ; __vbaObjSet
  loc_0040B4B0: mov edi, eax
  loc_0040B4B2: push FFFFFFFFh
  loc_0040B4B4: push edi
  loc_0040B4B5: mov eax, [edi]
  loc_0040B4B7: call [eax+0000005Ch]
  loc_0040B4BA: test eax, eax
  loc_0040B4BC: fnclex
  loc_0040B4BE: jge 0040B4CFh
  loc_0040B4C0: push 0000005Ch
  loc_0040B4C2: push 004056F4h
  loc_0040B4C7: push edi
  loc_0040B4C8: push eax
  loc_0040B4C9: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040B4CF: lea ecx, var_2C
  loc_0040B4D2: call ebx
  loc_0040B4D4: mov ecx, [esi]
  loc_0040B4D6: push esi
  loc_0040B4D7: call [ecx+0000032Ch]
  loc_0040B4DD: lea edx, var_2C
  loc_0040B4E0: push eax
  loc_0040B4E1: push edx
  loc_0040B4E2: call [00401080h] ; __vbaObjSet
  loc_0040B4E8: mov edi, eax
  loc_0040B4EA: push 00405714h ; "Loading Run Time Form, please wait"
  loc_0040B4EF: push edi
  loc_0040B4F0: mov eax, [edi]
  loc_0040B4F2: call [eax+00000054h]
  loc_0040B4F5: test eax, eax
  loc_0040B4F7: fnclex
  loc_0040B4F9: jge 0040B50Ah
  loc_0040B4FB: push 00000054h
  loc_0040B4FD: push 0040575Ch
  loc_0040B502: push edi
  loc_0040B503: push eax
  loc_0040B504: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040B50A: lea ecx, var_2C
  loc_0040B50D: call ebx
  loc_0040B50F: mov edi, [esi]
  loc_0040B511: mov ecx, 0000000Bh
  loc_0040B516: call [004010ECh] ; __vbaI2I4
  loc_0040B51C: push eax
  loc_0040B51D: push esi
  loc_0040B51E: call [edi+000000A4h]
  loc_0040B524: test eax, eax
  loc_0040B526: fnclex
  loc_0040B528: jge 0040B53Ch
  loc_0040B52A: push 000000A4h
  loc_0040B52F: push 00405120h
  loc_0040B534: push esi
  loc_0040B535: push eax
  loc_0040B536: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040B53C: call [004010A0h] ; rtcDoEvents
  loc_0040B542: mov eax, [00423054h]
  loc_0040B547: test eax, eax
  loc_0040B549: jnz 0040B55Bh
  loc_0040B54B: push 00423054h
  loc_0040B550: push 004033BCh
  loc_0040B555: call [00401168h] ; __vbaNew2
  loc_0040B55B: sub esp, 00000010h
  loc_0040B55E: mov eax, 0000000Ah
  loc_0040B563: mov ebx, esp
  loc_0040B565: mov edi, eax
  loc_0040B567: mov var_8C, edi
  loc_0040B56D: mov ecx, 80020004h
  loc_0040B572: mov [ebx], edi
  loc_0040B574: mov edi, var_88
  loc_0040B57A: mov edx, ecx
  loc_0040B57C: sub esp, 00000010h
  loc_0040B57F: mov [ebx+00000004h], edi
  loc_0040B582: mov var_84, edx
  loc_0040B588: mov esi, [00423054h]
  loc_0040B58E: mov var_7C, eax
  loc_0040B591: mov edi, var_7C
  loc_0040B594: mov [ebx+00000008h], edx
  loc_0040B597: mov edx, var_80
  loc_0040B59A: mov var_74, ecx
  loc_0040B59D: mov [ebx+0000000Ch], edx
  loc_0040B5A0: mov edx, esp
  loc_0040B5A2: mov eax, [esi]
  loc_0040B5A4: push esi
  loc_0040B5A5: mov [edx], edi
  loc_0040B5A7: mov edi, var_78
  loc_0040B5AA: mov [edx+00000004h], edi
  loc_0040B5AD: mov [edx+00000008h], ecx
  loc_0040B5B0: mov ecx, var_70
  loc_0040B5B3: mov [edx+0000000Ch], ecx
  loc_0040B5B6: call [eax+000002B0h]
  loc_0040B5BC: test eax, eax
  loc_0040B5BE: fnclex
  loc_0040B5C0: jge 0040B5D4h
  loc_0040B5C2: push 000002B0h
  loc_0040B5C7: push 0040576Ch
  loc_0040B5CC: push esi
  loc_0040B5CD: push eax
  loc_0040B5CE: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040B5D4: mov var_4, 00000000h
  loc_0040B5DB: push 0040B62Fh
  loc_0040B5E0: jmp 0040B61Eh
  loc_0040B5E2: lea edx, var_28
  loc_0040B5E5: lea eax, var_24
  loc_0040B5E8: push edx
  loc_0040B5E9: lea ecx, var_20
  loc_0040B5EC: push eax
  loc_0040B5ED: push ecx
  loc_0040B5EE: push 00000003h
  loc_0040B5F0: call [00401180h] ; __vbaFreeStrList
  loc_0040B5F6: add esp, 00000010h
  loc_0040B5F9: lea ecx, var_2C
  loc_0040B5FC: call [004011F0h] ; __vbaFreeObj
  loc_0040B602: lea edx, var_6C
  loc_0040B605: lea eax, var_5C
  loc_0040B608: push edx
  loc_0040B609: lea ecx, var_4C
  loc_0040B60C: push eax
  loc_0040B60D: lea edx, var_3C
  loc_0040B610: push ecx
  loc_0040B611: push edx
  loc_0040B612: push 00000004h
  loc_0040B614: call [00401038h] ; __vbaFreeVarList
  loc_0040B61A: add esp, 00000014h
  loc_0040B61D: ret
  loc_0040B61E: mov esi, [004011F4h] ; __vbaFreeStr
  loc_0040B624: lea ecx, var_18
  loc_0040B627: call __vbaFreeStr
  loc_0040B629: lea ecx, var_1C
  loc_0040B62C: call __vbaFreeStr
  loc_0040B62E: ret
  loc_0040B62F: mov eax, Me
  loc_0040B632: push eax
  loc_0040B633: mov ecx, [eax]
  loc_0040B635: call [ecx+00000008h]
  loc_0040B638: mov eax, var_4
  loc_0040B63B: mov ecx, var_14
  loc_0040B63E: pop edi
  loc_0040B63F: pop esi
  loc_0040B640: mov fs:[00000000h], ecx
  loc_0040B647: pop ebx
  loc_0040B648: mov esp, ebp
  loc_0040B64A: pop ebp
  loc_0040B64B: retn 0004h
End Sub

Private Sub Option1_Click() '40C380
  loc_0040C380: push ebp
  loc_0040C381: mov ebp, esp
  loc_0040C383: sub esp, 0000000Ch
  loc_0040C386: push 00401AA6h ; __vbaExceptHandler
  loc_0040C38B: mov eax, fs:[00000000h]
  loc_0040C391: push eax
  loc_0040C392: mov fs:[00000000h], esp
  loc_0040C399: sub esp, 0000000Ch
  loc_0040C39C: push ebx
  loc_0040C39D: push esi
  loc_0040C39E: push edi
  loc_0040C39F: mov var_C, esp
  loc_0040C3A2: mov var_8, 00401240h
  loc_0040C3A9: mov esi, Me
  loc_0040C3AC: mov eax, esi
  loc_0040C3AE: and eax, 00000001h
  loc_0040C3B1: mov var_4, eax
  loc_0040C3B4: and esi, FFFFFFFEh
  loc_0040C3B7: push esi
  loc_0040C3B8: mov Me, esi
  loc_0040C3BB: mov ecx, [esi]
  loc_0040C3BD: call [ecx+00000004h]
  loc_0040C3C0: mov edx, [esi]
  loc_0040C3C2: lea eax, var_18
  loc_0040C3C5: xor edi, edi
  loc_0040C3C7: push eax
  loc_0040C3C8: mov var_18, edi
  loc_0040C3CB: push esi
  loc_0040C3CC: mov var_18, 00000001h
  loc_0040C3D3: call [edx+00000708h]
  loc_0040C3D9: mov var_4, edi
  loc_0040C3DC: mov eax, Me
  loc_0040C3DF: push eax
  loc_0040C3E0: mov ecx, [eax]
  loc_0040C3E2: call [ecx+00000008h]
  loc_0040C3E5: mov eax, var_4
  loc_0040C3E8: mov ecx, var_14
  loc_0040C3EB: pop edi
  loc_0040C3EC: pop esi
  loc_0040C3ED: mov fs:[00000000h], ecx
  loc_0040C3F4: pop ebx
  loc_0040C3F5: mov esp, ebp
  loc_0040C3F7: pop ebp
  loc_0040C3F8: retn 0004h
End Sub

Private Sub Form_Load() '40B650
  loc_0040B650: push ebp
  loc_0040B651: mov ebp, esp
  loc_0040B653: sub esp, 0000000Ch
  loc_0040B656: push 00401AA6h ; __vbaExceptHandler
  loc_0040B65B: mov eax, fs:[00000000h]
  loc_0040B661: push eax
  loc_0040B662: mov fs:[00000000h], esp
  loc_0040B669: sub esp, 00000168h
  loc_0040B66F: push ebx
  loc_0040B670: push esi
  loc_0040B671: push edi
  loc_0040B672: mov var_C, esp
  loc_0040B675: mov var_8, 00401220h
  loc_0040B67C: mov edi, Me
  loc_0040B67F: mov eax, edi
  loc_0040B681: and eax, 00000001h
  loc_0040B684: mov var_4, eax
  loc_0040B687: and edi, FFFFFFFEh
  loc_0040B68A: push edi
  loc_0040B68B: mov Me, edi
  loc_0040B68E: mov ecx, [edi]
  loc_0040B690: call [ecx+00000004h]
  loc_0040B693: mov edx, [edi]
  loc_0040B695: xor esi, esi
  loc_0040B697: push edi
  loc_0040B698: mov var_18, esi
  loc_0040B69B: mov var_1C, esi
  loc_0040B69E: mov var_20, esi
  loc_0040B6A1: mov var_24, esi
  loc_0040B6A4: mov var_28, esi
  loc_0040B6A7: mov var_2C, esi
  loc_0040B6AA: mov var_30, esi
  loc_0040B6AD: mov var_40, esi
  loc_0040B6B0: mov var_50, esi
  loc_0040B6B3: mov var_60, esi
  loc_0040B6B6: mov var_70, esi
  loc_0040B6B9: mov var_80, esi
  loc_0040B6BC: mov var_90, esi
  loc_0040B6C2: mov var_A0, esi
  loc_0040B6C8: mov var_B0, esi
  loc_0040B6CE: mov var_C0, esi
  loc_0040B6D4: mov var_D0, esi
  loc_0040B6DA: mov var_E0, esi
  loc_0040B6E0: mov var_F0, esi
  loc_0040B6E6: mov var_100, esi
  loc_0040B6EC: mov var_110, esi
  loc_0040B6F2: mov var_124, esi
  loc_0040B6F8: mov var_128, esi
  loc_0040B6FE: mov var_12C, esi
  loc_0040B704: mov var_130, esi
  loc_0040B70A: call [edx+0000031Ch]
  loc_0040B710: mov ebx, [00401080h] ; __vbaObjSet
  loc_0040B716: push eax
  loc_0040B717: lea eax, var_24
  loc_0040B71A: push eax
  loc_0040B71B: call ebx
  loc_0040B71D: mov ecx, [eax]
  loc_0040B71F: push FFFFFFFFh
  loc_0040B721: push eax
  loc_0040B722: mov var_134, eax
  loc_0040B728: call [ecx+000000E4h]
  loc_0040B72E: cmp eax, esi
  loc_0040B730: fnclex
  loc_0040B732: jge 0040B74Ch
  loc_0040B734: mov edx, var_134
  loc_0040B73A: push 000000E4h
  loc_0040B73F: push 00405388h
  loc_0040B744: push edx
  loc_0040B745: push eax
  loc_0040B746: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040B74C: lea ecx, var_24
  loc_0040B74F: call [004011F0h] ; __vbaFreeObj
  loc_0040B755: mov eax, [edi]
  loc_0040B757: lea ecx, var_130
  loc_0040B75D: push ecx
  loc_0040B75E: push edi
  loc_0040B75F: mov var_130, 00000001h
  loc_0040B769: call [eax+00000708h]
  loc_0040B76F: lea edx, var_F0
  loc_0040B775: lea ecx, var_40
  loc_0040B778: mov var_E8, 00405A68h ; "C:\ProbeRecipe\LampElectrical\*.PMA"
  loc_0040B782: mov var_F0, 00000008h
  loc_0040B78C: call [004011B4h] ; __vbaVarDup
  loc_0040B792: lea edx, var_40
  loc_0040B795: push esi
  loc_0040B796: push edx
  loc_0040B797: call [00401150h] ; rtcDir
  loc_0040B79D: mov edx, eax
  loc_0040B79F: lea ecx, var_1C
  loc_0040B7A2: call [004011D0h] ; __vbaStrMove
  loc_0040B7A8: lea ecx, var_40
  loc_0040B7AB: call [00401020h] ; __vbaFreeVar
  loc_0040B7B1: mov eax, var_1C
  loc_0040B7B4: push eax
  loc_0040B7B5: push esi
  loc_0040B7B6: call [004010DCh] ; __vbaStrCmp
  loc_0040B7BC: test eax, eax
  loc_0040B7BE: jnz 0040B8DBh
  loc_0040B7C4: mov ecx, [edi]
  loc_0040B7C6: push edi
  loc_0040B7C7: call [ecx+00000304h]
  loc_0040B7CD: lea edx, var_24
  loc_0040B7D0: push eax
  loc_0040B7D1: push edx
  loc_0040B7D2: call ebx
  loc_0040B7D4: sub esp, 00000010h
  loc_0040B7D7: mov esi, eax
  loc_0040B7D9: mov edx, esp
  loc_0040B7DB: mov eax, 0000000Ah
  loc_0040B7E0: mov var_F0, eax
  loc_0040B7E6: mov var_E8, 80020004h
  loc_0040B7F0: mov ecx, [esi]
  loc_0040B7F2: mov [edx], eax
  loc_0040B7F4: mov eax, var_EC
  loc_0040B7FA: push 004055D0h ; "ERROR"
  loc_0040B7FF: mov [edx+00000004h], eax
  loc_0040B802: mov eax, var_E8
  loc_0040B808: push esi
  loc_0040B809: mov [edx+00000008h], eax
  loc_0040B80C: mov eax, var_E4
  loc_0040B812: mov [edx+0000000Ch], eax
  loc_0040B815: call [ecx+000001ECh]
  loc_0040B81B: test eax, eax
  loc_0040B81D: fnclex
  loc_0040B81F: jge 0040B833h
  loc_0040B821: push 000001ECh
  loc_0040B826: push 004055DCh
  loc_0040B82B: push esi
  loc_0040B82C: push eax
  loc_0040B82D: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040B833: lea ecx, var_24
  loc_0040B836: call [004011F0h] ; __vbaFreeObj
  loc_0040B83C: xor esi, esi
  loc_0040B83E: mov ecx, [edi]
  loc_0040B840: push edi
  loc_0040B841: call [ecx+00000304h]
  loc_0040B847: lea edx, var_24
  loc_0040B84A: push eax
  loc_0040B84B: push edx
  loc_0040B84C: call ebx
  loc_0040B84E: mov ecx, [eax]
  loc_0040B850: push esi
  loc_0040B851: push eax
  loc_0040B852: mov var_134, eax
  loc_0040B858: call [ecx+000000F4h]
  loc_0040B85E: cmp eax, esi
  loc_0040B860: fnclex
  loc_0040B862: jge 0040B87Ch
  loc_0040B864: mov edx, var_134
  loc_0040B86A: push 000000F4h
  loc_0040B86F: push 004055DCh
  loc_0040B874: push edx
  loc_0040B875: push eax
  loc_0040B876: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040B87C: lea ecx, var_24
  loc_0040B87F: call [004011F0h] ; __vbaFreeObj
  loc_0040B885: mov eax, [edi]
  loc_0040B887: push edi
  loc_0040B888: call [eax+000002FCh]
  loc_0040B88E: lea ecx, var_24
  loc_0040B891: push eax
  loc_0040B892: push ecx
  loc_0040B893: call ebx
  loc_0040B895: mov esi, [eax]
  loc_0040B897: mov ecx, 00000001h
  loc_0040B89C: mov var_134, eax
  loc_0040B8A2: call [004010ECh] ; __vbaI2I4
  loc_0040B8A8: mov edx, esi
  loc_0040B8AA: mov esi, var_134
  loc_0040B8B0: push eax
  loc_0040B8B1: push esi
  loc_0040B8B2: call [edx+000000E4h]
  loc_0040B8B8: test eax, eax
  loc_0040B8BA: fnclex
  loc_0040B8BC: jge 0040B9F6h
  loc_0040B8C2: push 000000E4h
  loc_0040B8C7: push 00405354h
  loc_0040B8CC: push esi
  loc_0040B8CD: mov esi, [0040105Ch] ; __vbaHresultCheckObj
  loc_0040B8D3: push eax
  loc_0040B8D4: call __vbaHresultCheckObj
  loc_0040B8D6: jmp 0040B9FCh
  loc_0040B8DB: mov ecx, var_1C
  loc_0040B8DE: push ecx
  loc_0040B8DF: push esi
  loc_0040B8E0: call [004010DCh] ; __vbaStrCmp
  loc_0040B8E6: test eax, eax
  loc_0040B8E8: jz 0040B83Eh
  loc_0040B8EE: mov eax, var_1C
  loc_0040B8F1: push 00000001h
  loc_0040B8F3: push eax
  loc_0040B8F4: lea edx, var_1C
  loc_0040B8F7: push 00405AB4h ; "."
  loc_0040B8FC: push esi
  loc_0040B8FD: mov var_E8, edx
  loc_0040B903: mov var_F0, 00004008h
  loc_0040B90D: call [0040116Ch] ; __vbaInStr
  loc_0040B913: sub eax, 00000001h
  loc_0040B916: lea ecx, var_F0
  loc_0040B91C: jo 0040C093h
  loc_0040B922: push eax
  loc_0040B923: lea edx, var_40
  loc_0040B926: push ecx
  loc_0040B927: push edx
  loc_0040B928: call [004011C4h] ; rtcLeftCharVar
  loc_0040B92E: mov eax, [edi]
  loc_0040B930: push edi
  loc_0040B931: call [eax+00000304h]
  loc_0040B937: lea ecx, var_24
  loc_0040B93A: push eax
  loc_0040B93B: push ecx
  loc_0040B93C: call ebx
  loc_0040B93E: sub esp, 00000010h
  loc_0040B941: mov ecx, 0000000Ah
  loc_0040B946: mov edx, esp
  loc_0040B948: mov var_100, ecx
  loc_0040B94E: mov esi, eax
  loc_0040B950: mov eax, 80020004h
  loc_0040B955: mov [edx], ecx
  loc_0040B957: mov ecx, var_FC
  loc_0040B95D: mov var_F8, eax
  loc_0040B963: mov ebx, [esi]
  loc_0040B965: mov [edx+00000004h], ecx
  loc_0040B968: lea ecx, var_40
  loc_0040B96B: push ecx
  loc_0040B96C: mov [edx+00000008h], eax
  loc_0040B96F: mov eax, var_F4
  loc_0040B975: mov [edx+0000000Ch], eax
  loc_0040B978: lea edx, var_20
  loc_0040B97B: push edx
  loc_0040B97C: call [00401148h] ; __vbaStrVarVal
  loc_0040B982: push eax
  loc_0040B983: push esi
  loc_0040B984: call [ebx+000001ECh]
  loc_0040B98A: test eax, eax
  loc_0040B98C: fnclex
  loc_0040B98E: jge 0040B9A2h
  loc_0040B990: push 000001ECh
  loc_0040B995: push 004055DCh
  loc_0040B99A: push esi
  loc_0040B99B: push eax
  loc_0040B99C: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040B9A2: lea ecx, var_20
  loc_0040B9A5: call [004011F4h] ; __vbaFreeStr
  loc_0040B9AB: lea ecx, var_24
  loc_0040B9AE: call [004011F0h] ; __vbaFreeObj
  loc_0040B9B4: mov esi, [00401020h] ; __vbaFreeVar
  loc_0040B9BA: lea ecx, var_40
  loc_0040B9BD: call __vbaFreeVar
  loc_0040B9BF: lea eax, var_40
  loc_0040B9C2: push 00000000h
  loc_0040B9C4: push eax
  loc_0040B9C5: mov var_38, 80020004h
  loc_0040B9CC: mov var_40, 0000000Ah
  loc_0040B9D3: call [00401150h] ; rtcDir
  loc_0040B9D9: mov edx, eax
  loc_0040B9DB: lea ecx, var_1C
  loc_0040B9DE: call [004011D0h] ; __vbaStrMove
  loc_0040B9E4: lea ecx, var_40
  loc_0040B9E7: call __vbaFreeVar
  loc_0040B9E9: mov ebx, [00401080h] ; __vbaObjSet
  loc_0040B9EF: xor esi, esi
  loc_0040B9F1: jmp 0040B8DBh
  loc_0040B9F6: mov esi, [0040105Ch] ; __vbaHresultCheckObj
  loc_0040B9FC: lea ecx, var_24
  loc_0040B9FF: call [004011F0h] ; __vbaFreeObj
  loc_0040BA05: mov eax, [edi]
  loc_0040BA07: push edi
  loc_0040BA08: call [eax+000006FCh]
  loc_0040BA0E: test eax, eax
  loc_0040BA10: jge 0040BA20h
  loc_0040BA12: push 000006FCh
  loc_0040BA17: push 00405150h
  loc_0040BA1C: push edi
  loc_0040BA1D: push eax
  loc_0040BA1E: call __vbaHresultCheckObj
  loc_0040BA20: mov ecx, [edi]
  loc_0040BA22: push edi
  loc_0040BA23: call [ecx+00000328h]
  loc_0040BA29: lea edx, var_30
  loc_0040BA2C: push eax
  loc_0040BA2D: push edx
  loc_0040BA2E: call ebx
  loc_0040BA30: mov var_164, eax
  loc_0040BA36: mov eax, [0042351Ch]
  loc_0040BA3B: test eax, eax
  loc_0040BA3D: mov var_E8, 00405ABCh ; "Software rev: "
  loc_0040BA47: mov var_F0, 00000008h
  loc_0040BA51: jnz 0040BA63h
  loc_0040BA53: push 0042351Ch
  loc_0040BA58: push 00405AFCh
  loc_0040BA5D: call [00401168h] ; __vbaNew2
  loc_0040BA63: mov ebx, [0042351Ch]
  loc_0040BA69: lea ecx, var_24
  loc_0040BA6C: push ecx
  loc_0040BA6D: push ebx
  loc_0040BA6E: mov eax, [ebx]
  loc_0040BA70: call [eax+00000014h]
  loc_0040BA73: test eax, eax
  loc_0040BA75: fnclex
  loc_0040BA77: jge 0040BA84h
  loc_0040BA79: push 00000014h
  loc_0040BA7B: push 00405AECh
  loc_0040BA80: push ebx
  loc_0040BA81: push eax
  loc_0040BA82: call __vbaHresultCheckObj
  loc_0040BA84: mov eax, var_24
  loc_0040BA87: lea ecx, var_124
  loc_0040BA8D: push ecx
  loc_0040BA8E: push eax
  loc_0040BA8F: mov edx, [eax]
  loc_0040BA91: mov ebx, eax
  loc_0040BA93: call [edx+000000B8h]
  loc_0040BA99: test eax, eax
  loc_0040BA9B: fnclex
  loc_0040BA9D: jge 0040BAADh
  loc_0040BA9F: push 000000B8h
  loc_0040BAA4: push 00405B0Ch
  loc_0040BAA9: push ebx
  loc_0040BAAA: push eax
  loc_0040BAAB: call __vbaHresultCheckObj
  loc_0040BAAD: mov edx, var_124
  loc_0040BAB3: push edx
  loc_0040BAB4: call [00401004h] ; __vbaStrI2
  loc_0040BABA: mov var_38, eax
  loc_0040BABD: lea eax, var_40
  loc_0040BAC0: lea ecx, var_50
  loc_0040BAC3: mov ebx, 00000008h
  loc_0040BAC8: push eax
  loc_0040BAC9: push ecx
  loc_0040BACA: mov var_40, ebx
  loc_0040BACD: call [004010A4h] ; rtcTrimVar
  loc_0040BAD3: mov eax, [0042351Ch]
  loc_0040BAD8: mov var_F8, 00405AB4h ; "."
  loc_0040BAE2: test eax, eax
  loc_0040BAE4: mov var_100, ebx
  loc_0040BAEA: jnz 0040BAFCh
  loc_0040BAEC: push 0042351Ch
  loc_0040BAF1: push 00405AFCh
  loc_0040BAF6: call [00401168h] ; __vbaNew2
  loc_0040BAFC: mov ebx, [0042351Ch]
  loc_0040BB02: lea eax, var_28
  loc_0040BB05: push eax
  loc_0040BB06: push ebx
  loc_0040BB07: mov edx, [ebx]
  loc_0040BB09: call [edx+00000014h]
  loc_0040BB0C: test eax, eax
  loc_0040BB0E: fnclex
  loc_0040BB10: jge 0040BB1Dh
  loc_0040BB12: push 00000014h
  loc_0040BB14: push 00405AECh
  loc_0040BB19: push ebx
  loc_0040BB1A: push eax
  loc_0040BB1B: call __vbaHresultCheckObj
  loc_0040BB1D: mov eax, var_28
  loc_0040BB20: lea edx, var_128
  loc_0040BB26: push edx
  loc_0040BB27: push eax
  loc_0040BB28: mov ecx, [eax]
  loc_0040BB2A: mov ebx, eax
  loc_0040BB2C: call [ecx+000000C0h]
  loc_0040BB32: test eax, eax
  loc_0040BB34: fnclex
  loc_0040BB36: jge 0040BB46h
  loc_0040BB38: push 000000C0h
  loc_0040BB3D: push 00405B0Ch
  loc_0040BB42: push ebx
  loc_0040BB43: push eax
  loc_0040BB44: call __vbaHresultCheckObj
  loc_0040BB46: mov eax, var_128
  loc_0040BB4C: push eax
  loc_0040BB4D: call [00401004h] ; __vbaStrI2
  loc_0040BB53: lea ecx, var_80
  loc_0040BB56: lea edx, var_90
  loc_0040BB5C: mov ebx, 00000008h
  loc_0040BB61: push ecx
  loc_0040BB62: push edx
  loc_0040BB63: mov var_78, eax
  loc_0040BB66: mov var_80, ebx
  loc_0040BB69: call [004010A4h] ; rtcTrimVar
  loc_0040BB6F: mov eax, [0042351Ch]
  loc_0040BB74: mov var_108, 00405AB4h ; "."
  loc_0040BB7E: test eax, eax
  loc_0040BB80: mov var_110, ebx
  loc_0040BB86: jnz 0040BB98h
  loc_0040BB88: push 0042351Ch
  loc_0040BB8D: push 00405AFCh
  loc_0040BB92: call [00401168h] ; __vbaNew2
  loc_0040BB98: mov ebx, [0042351Ch]
  loc_0040BB9E: lea ecx, var_2C
  loc_0040BBA1: push ecx
  loc_0040BBA2: push ebx
  loc_0040BBA3: mov eax, [ebx]
  loc_0040BBA5: call [eax+00000014h]
  loc_0040BBA8: test eax, eax
  loc_0040BBAA: fnclex
  loc_0040BBAC: jge 0040BBB9h
  loc_0040BBAE: push 00000014h
  loc_0040BBB0: push 00405AECh
  loc_0040BBB5: push ebx
  loc_0040BBB6: push eax
  loc_0040BBB7: call __vbaHresultCheckObj
  loc_0040BBB9: mov eax, var_2C
  loc_0040BBBC: lea ecx, var_12C
  loc_0040BBC2: push ecx
  loc_0040BBC3: push eax
  loc_0040BBC4: mov edx, [eax]
  loc_0040BBC6: mov ebx, eax
  loc_0040BBC8: call [edx+000000C8h]
  loc_0040BBCE: test eax, eax
  loc_0040BBD0: fnclex
  loc_0040BBD2: jge 0040BBE2h
  loc_0040BBD4: push 000000C8h
  loc_0040BBD9: push 00405B0Ch
  loc_0040BBDE: push ebx
  loc_0040BBDF: push eax
  loc_0040BBE0: call __vbaHresultCheckObj
  loc_0040BBE2: mov edx, var_12C
  loc_0040BBE8: push edx
  loc_0040BBE9: call [00401004h] ; __vbaStrI2
  loc_0040BBEF: mov var_B8, eax
  loc_0040BBF5: lea eax, var_C0
  loc_0040BBFB: lea ecx, var_D0
  loc_0040BC01: push eax
  loc_0040BC02: push ecx
  loc_0040BC03: mov var_C0, 00000008h
  loc_0040BC0D: call [004010A4h] ; rtcTrimVar
  loc_0040BC13: mov edx, var_164
  loc_0040BC19: mov esi, [004011ACh] ; __vbaVarAdd
  loc_0040BC1F: lea eax, var_F0
  loc_0040BC25: lea ecx, var_50
  loc_0040BC28: mov ebx, [edx]
  loc_0040BC2A: push eax
  loc_0040BC2B: lea edx, var_60
  loc_0040BC2E: push ecx
  loc_0040BC2F: push edx
  loc_0040BC30: call __vbaVarAdd
  loc_0040BC32: push eax
  loc_0040BC33: lea eax, var_100
  loc_0040BC39: lea ecx, var_70
  loc_0040BC3C: push eax
  loc_0040BC3D: push ecx
  loc_0040BC3E: call __vbaVarAdd
  loc_0040BC40: push eax
  loc_0040BC41: lea edx, var_90
  loc_0040BC47: lea eax, var_A0
  loc_0040BC4D: push edx
  loc_0040BC4E: push eax
  loc_0040BC4F: call __vbaVarAdd
  loc_0040BC51: lea ecx, var_110
  loc_0040BC57: push eax
  loc_0040BC58: lea edx, var_B0
  loc_0040BC5E: push ecx
  loc_0040BC5F: push edx
  loc_0040BC60: call __vbaVarAdd
  loc_0040BC62: push eax
  loc_0040BC63: lea eax, var_D0
  loc_0040BC69: lea ecx, var_E0
  loc_0040BC6F: push eax
  loc_0040BC70: push ecx
  loc_0040BC71: call __vbaVarAdd
  loc_0040BC73: lea edx, var_20
  loc_0040BC76: push eax
  loc_0040BC77: push edx
  loc_0040BC78: call [00401148h] ; __vbaStrVarVal
  loc_0040BC7E: mov var_17C, ebx
  loc_0040BC84: mov ebx, var_164
  loc_0040BC8A: push eax
  loc_0040BC8B: mov eax, var_17C
  loc_0040BC91: push ebx
  loc_0040BC92: call [eax+00000054h]
  loc_0040BC95: test eax, eax
  loc_0040BC97: fnclex
  loc_0040BC99: jge 0040BCAAh
  loc_0040BC9B: push 00000054h
  loc_0040BC9D: push 0040575Ch
  loc_0040BCA2: push ebx
  loc_0040BCA3: push eax
  loc_0040BCA4: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040BCAA: lea ecx, var_20
  loc_0040BCAD: call [004011F4h] ; __vbaFreeStr
  loc_0040BCB3: lea ecx, var_30
  loc_0040BCB6: lea edx, var_2C
  loc_0040BCB9: push ecx
  loc_0040BCBA: lea eax, var_28
  loc_0040BCBD: push edx
  loc_0040BCBE: lea ecx, var_24
  loc_0040BCC1: push eax
  loc_0040BCC2: push ecx
  loc_0040BCC3: push 00000004h
  loc_0040BCC5: call [00401040h] ; __vbaFreeObjList
  loc_0040BCCB: lea edx, var_E0
  loc_0040BCD1: lea eax, var_D0
  loc_0040BCD7: push edx
  loc_0040BCD8: lea ecx, var_B0
  loc_0040BCDE: push eax
  loc_0040BCDF: lea edx, var_C0
  loc_0040BCE5: push ecx
  loc_0040BCE6: lea eax, var_A0
  loc_0040BCEC: push edx
  loc_0040BCED: lea ecx, var_90
  loc_0040BCF3: push eax
  loc_0040BCF4: lea edx, var_70
  loc_0040BCF7: push ecx
  loc_0040BCF8: lea eax, var_80
  loc_0040BCFB: push edx
  loc_0040BCFC: lea ecx, var_60
  loc_0040BCFF: push eax
  loc_0040BD00: lea edx, var_50
  loc_0040BD03: push ecx
  loc_0040BD04: lea eax, var_40
  loc_0040BD07: push edx
  loc_0040BD08: push eax
  loc_0040BD09: push 0000000Bh
  loc_0040BD0B: call [00401038h] ; __vbaFreeVarList
  loc_0040BD11: mov eax, [0042351Ch]
  loc_0040BD16: add esp, 00000044h
  loc_0040BD19: test eax, eax
  loc_0040BD1B: jnz 0040BD2Dh
  loc_0040BD1D: push 0042351Ch
  loc_0040BD22: push 00405AFCh
  loc_0040BD27: call [00401168h] ; __vbaNew2
  loc_0040BD2D: mov ebx, [0042351Ch]
  loc_0040BD33: lea edx, var_24
  loc_0040BD36: push edx
  loc_0040BD37: push ebx
  loc_0040BD38: mov ecx, [ebx]
  loc_0040BD3A: call [ecx+00000014h]
  loc_0040BD3D: test eax, eax
  loc_0040BD3F: fnclex
  loc_0040BD41: jge 0040BD52h
  loc_0040BD43: push 00000014h
  loc_0040BD45: push 00405AECh
  loc_0040BD4A: push ebx
  loc_0040BD4B: push eax
  loc_0040BD4C: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040BD52: mov eax, var_24
  loc_0040BD55: lea edx, var_124
  loc_0040BD5B: push edx
  loc_0040BD5C: push eax
  loc_0040BD5D: mov ecx, [eax]
  loc_0040BD5F: mov ebx, eax
  loc_0040BD61: call [ecx+000000B8h]
  loc_0040BD67: test eax, eax
  loc_0040BD69: fnclex
  loc_0040BD6B: jge 0040BD7Fh
  loc_0040BD6D: push 000000B8h
  loc_0040BD72: push 00405B0Ch
  loc_0040BD77: push ebx
  loc_0040BD78: push eax
  loc_0040BD79: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040BD7F: mov eax, var_124
  loc_0040BD85: push eax
  loc_0040BD86: call [00401004h] ; __vbaStrI2
  loc_0040BD8C: lea ecx, var_40
  loc_0040BD8F: lea edx, var_50
  loc_0040BD92: mov ebx, 00000008h
  loc_0040BD97: push ecx
  loc_0040BD98: push edx
  loc_0040BD99: mov var_38, eax
  loc_0040BD9C: mov var_40, ebx
  loc_0040BD9F: call [004010A4h] ; rtcTrimVar
  loc_0040BDA5: mov eax, [0042351Ch]
  loc_0040BDAA: mov var_E8, 00405AB4h ; "."
  loc_0040BDB4: test eax, eax
  loc_0040BDB6: mov var_F0, ebx
  loc_0040BDBC: jnz 0040BDCEh
  loc_0040BDBE: push 0042351Ch
  loc_0040BDC3: push 00405AFCh
  loc_0040BDC8: call [00401168h] ; __vbaNew2
  loc_0040BDCE: mov ebx, [0042351Ch]
  loc_0040BDD4: lea ecx, var_28
  loc_0040BDD7: push ecx
  loc_0040BDD8: push ebx
  loc_0040BDD9: mov eax, [ebx]
  loc_0040BDDB: call [eax+00000014h]
  loc_0040BDDE: test eax, eax
  loc_0040BDE0: fnclex
  loc_0040BDE2: jge 0040BDF3h
  loc_0040BDE4: push 00000014h
  loc_0040BDE6: push 00405AECh
  loc_0040BDEB: push ebx
  loc_0040BDEC: push eax
  loc_0040BDED: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040BDF3: mov eax, var_28
  loc_0040BDF6: lea ecx, var_128
  loc_0040BDFC: push ecx
  loc_0040BDFD: push eax
  loc_0040BDFE: mov edx, [eax]
  loc_0040BE00: mov ebx, eax
  loc_0040BE02: call [edx+000000C0h]
  loc_0040BE08: test eax, eax
  loc_0040BE0A: fnclex
  loc_0040BE0C: jge 0040BE24h
  loc_0040BE0E: push 000000C0h
  loc_0040BE13: push 00405B0Ch
  loc_0040BE18: push ebx
  loc_0040BE19: mov ebx, [0040105Ch] ; __vbaHresultCheckObj
  loc_0040BE1F: push eax
  loc_0040BE20: call ebx
  loc_0040BE22: jmp 0040BE2Ah
  loc_0040BE24: mov ebx, [0040105Ch] ; __vbaHresultCheckObj
  loc_0040BE2A: mov edx, var_128
  loc_0040BE30: push edx
  loc_0040BE31: call [00401004h] ; __vbaStrI2
  loc_0040BE37: mov var_68, eax
  loc_0040BE3A: lea eax, var_70
  loc_0040BE3D: lea ecx, var_80
  loc_0040BE40: push eax
  loc_0040BE41: push ecx
  loc_0040BE42: mov var_70, 00000008h
  loc_0040BE49: call [004010A4h] ; rtcTrimVar
  loc_0040BE4F: lea edx, var_50
  loc_0040BE52: lea eax, var_F0
  loc_0040BE58: push edx
  loc_0040BE59: lea ecx, var_60
  loc_0040BE5C: push eax
  loc_0040BE5D: push ecx
  loc_0040BE5E: mov var_F8, 00405B20h ; "9.9"
  loc_0040BE68: mov var_100, 00008008h
  loc_0040BE72: call __vbaVarAdd
  loc_0040BE74: push eax
  loc_0040BE75: lea edx, var_80
  loc_0040BE78: lea eax, var_90
  loc_0040BE7E: push edx
  loc_0040BE7F: push eax
  loc_0040BE80: call __vbaVarAdd
  loc_0040BE82: lea ecx, var_100
  loc_0040BE88: push eax
  loc_0040BE89: push ecx
  loc_0040BE8A: call [004010E4h] ; __vbaVarTstEq
  loc_0040BE90: mov esi, eax
  loc_0040BE92: lea edx, var_28
  loc_0040BE95: lea eax, var_24
  loc_0040BE98: push edx
  loc_0040BE99: push eax
  loc_0040BE9A: push 00000002h
  loc_0040BE9C: call [00401040h] ; __vbaFreeObjList
  loc_0040BEA2: lea ecx, var_90
  loc_0040BEA8: lea edx, var_80
  loc_0040BEAB: push ecx
  loc_0040BEAC: lea eax, var_60
  loc_0040BEAF: push edx
  loc_0040BEB0: lea ecx, var_70
  loc_0040BEB3: push eax
  loc_0040BEB4: lea edx, var_50
  loc_0040BEB7: push ecx
  loc_0040BEB8: lea eax, var_40
  loc_0040BEBB: push edx
  loc_0040BEBC: push eax
  loc_0040BEBD: push 00000006h
  loc_0040BEBF: call [00401038h] ; __vbaFreeVarList
  loc_0040BEC5: mov ecx, [edi]
  loc_0040BEC7: add esp, 00000028h
  loc_0040BECA: test si, si
  loc_0040BECD: push edi
  loc_0040BECE: jz 0040BEF6h
  loc_0040BED0: call [ecx+00000324h]
  loc_0040BED6: lea edx, var_24
  loc_0040BED9: push eax
  loc_0040BEDA: push edx
  loc_0040BEDB: call [00401080h] ; __vbaObjSet
  loc_0040BEE1: mov esi, eax
  loc_0040BEE3: push FFFFFFFFh
  loc_0040BEE5: push esi
  loc_0040BEE6: mov eax, [esi]
  loc_0040BEE8: call [eax+0000009Ch]
  loc_0040BEEE: test eax, eax
  loc_0040BEF0: fnclex
  loc_0040BEF2: jge 0040BF28h
  loc_0040BEF4: jmp 0040BF1Ah
  loc_0040BEF6: call [ecx+00000324h]
  loc_0040BEFC: lea edx, var_24
  loc_0040BEFF: push eax
  loc_0040BF00: push edx
  loc_0040BF01: call [00401080h] ; __vbaObjSet
  loc_0040BF07: mov esi, eax
  loc_0040BF09: push 00000000h
  loc_0040BF0B: push esi
  loc_0040BF0C: mov eax, [esi]
  loc_0040BF0E: call [eax+0000009Ch]
  loc_0040BF14: test eax, eax
  loc_0040BF16: fnclex
  loc_0040BF18: jge 0040BF28h
  loc_0040BF1A: push 0000009Ch
  loc_0040BF1F: push 0040575Ch
  loc_0040BF24: push esi
  loc_0040BF25: push eax
  loc_0040BF26: call ebx
  loc_0040BF28: lea ecx, var_24
  loc_0040BF2B: call [004011F0h] ; __vbaFreeObj
  loc_0040BF31: mov ecx, [edi]
  loc_0040BF33: lea edx, var_20
  loc_0040BF36: push edx
  loc_0040BF37: push edi
  loc_0040BF38: call [ecx+000006F8h]
  loc_0040BF3E: xor esi, esi
  loc_0040BF40: cmp eax, esi
  loc_0040BF42: jge 0040BF52h
  loc_0040BF44: push 000006F8h
  loc_0040BF49: push 00405150h
  loc_0040BF4E: push edi
  loc_0040BF4F: push eax
  loc_0040BF50: call ebx
  loc_0040BF52: mov edx, var_20
  loc_0040BF55: lea ecx, var_18
  loc_0040BF58: mov var_20, esi
  loc_0040BF5B: call [004011D0h] ; __vbaStrMove
  loc_0040BF61: mov eax, var_18
  loc_0040BF64: push eax
  loc_0040BF65: push esi
  loc_0040BF66: call [004010DCh] ; __vbaStrCmp
  loc_0040BF6C: test eax, eax
  loc_0040BF6E: jz 0040BFEEh
  loc_0040BF70: mov ecx, 80020004h
  loc_0040BF75: mov eax, 0000000Ah
  loc_0040BF7A: mov var_58, ecx
  loc_0040BF7D: mov var_48, ecx
  loc_0040BF80: lea edx, var_100
  loc_0040BF86: lea ecx, var_40
  loc_0040BF89: mov var_60, eax
  loc_0040BF8C: mov var_50, eax
  loc_0040BF8F: mov var_F8, 004050E8h ; "IMT LampElectrical Probing"
  loc_0040BF99: mov var_100, 00000008h
  loc_0040BFA3: call [004011B4h] ; __vbaVarDup
  loc_0040BFA9: lea ecx, var_18
  loc_0040BFAC: lea edx, var_60
  loc_0040BFAF: mov var_E8, ecx
  loc_0040BFB5: lea eax, var_50
  loc_0040BFB8: push edx
  loc_0040BFB9: lea ecx, var_40
  loc_0040BFBC: push eax
  loc_0040BFBD: push ecx
  loc_0040BFBE: lea edx, var_F0
  loc_0040BFC4: push 00000030h
  loc_0040BFC6: push edx
  loc_0040BFC7: mov var_F0, 00004008h
  loc_0040BFD1: call [00401084h] ; rtcMsgBox
  loc_0040BFD7: lea eax, var_60
  loc_0040BFDA: lea ecx, var_50
  loc_0040BFDD: push eax
  loc_0040BFDE: lea edx, var_40
  loc_0040BFE1: push ecx
  loc_0040BFE2: push edx
  loc_0040BFE3: push 00000003h
  loc_0040BFE5: call [00401038h] ; __vbaFreeVarList
  loc_0040BFEB: add esp, 00000010h
  loc_0040BFEE: mov var_4, esi
  loc_0040BFF1: push 0040C074h
  loc_0040BFF6: jmp 0040C063h
  loc_0040BFF8: lea ecx, var_20
  loc_0040BFFB: call [004011F4h] ; __vbaFreeStr
  loc_0040C001: lea eax, var_30
  loc_0040C004: lea ecx, var_2C
  loc_0040C007: push eax
  loc_0040C008: lea edx, var_28
  loc_0040C00B: push ecx
  loc_0040C00C: lea eax, var_24
  loc_0040C00F: push edx
  loc_0040C010: push eax
  loc_0040C011: push 00000004h
  loc_0040C013: call [00401040h] ; __vbaFreeObjList
  loc_0040C019: lea ecx, var_E0
  loc_0040C01F: lea edx, var_D0
  loc_0040C025: push ecx
  loc_0040C026: lea eax, var_C0
  loc_0040C02C: push edx
  loc_0040C02D: lea ecx, var_B0
  loc_0040C033: push eax
  loc_0040C034: lea edx, var_A0
  loc_0040C03A: push ecx
  loc_0040C03B: lea eax, var_90
  loc_0040C041: push edx
  loc_0040C042: lea ecx, var_80
  loc_0040C045: push eax
  loc_0040C046: lea edx, var_70
  loc_0040C049: push ecx
  loc_0040C04A: lea eax, var_60
  loc_0040C04D: push edx
  loc_0040C04E: lea ecx, var_50
  loc_0040C051: push eax
  loc_0040C052: lea edx, var_40
  loc_0040C055: push ecx
  loc_0040C056: push edx
  loc_0040C057: push 0000000Bh
  loc_0040C059: call [00401038h] ; __vbaFreeVarList
  loc_0040C05F: add esp, 00000044h
  loc_0040C062: ret
  loc_0040C063: mov esi, [004011F4h] ; __vbaFreeStr
  loc_0040C069: lea ecx, var_18
  loc_0040C06C: call __vbaFreeStr
  loc_0040C06E: lea ecx, var_1C
  loc_0040C071: call __vbaFreeStr
  loc_0040C073: ret
  loc_0040C074: mov eax, Me
  loc_0040C077: push eax
  loc_0040C078: mov ecx, [eax]
  loc_0040C07A: call [ecx+00000008h]
  loc_0040C07D: mov eax, var_4
  loc_0040C080: mov ecx, var_14
  loc_0040C083: pop edi
  loc_0040C084: pop esi
  loc_0040C085: mov fs:[00000000h], ecx
  loc_0040C08C: pop ebx
  loc_0040C08D: mov esp, ebp
  loc_0040C08F: pop ebp
  loc_0040C090: retn 0004h
End Sub

Private Sub Timer1_Timer() '40C7E0
  loc_0040C7E0: push ebp
  loc_0040C7E1: mov ebp, esp
  loc_0040C7E3: sub esp, 0000000Ch
  loc_0040C7E6: push 00401AA6h ; __vbaExceptHandler
  loc_0040C7EB: mov eax, fs:[00000000h]
  loc_0040C7F1: push eax
  loc_0040C7F2: mov fs:[00000000h], esp
  loc_0040C7F9: sub esp, 00000028h
  loc_0040C7FC: push ebx
  loc_0040C7FD: push esi
  loc_0040C7FE: push edi
  loc_0040C7FF: mov var_C, esp
  loc_0040C802: mov var_8, 00401268h
  loc_0040C809: mov esi, Me
  loc_0040C80C: mov eax, esi
  loc_0040C80E: and eax, 00000001h
  loc_0040C811: mov var_4, eax
  loc_0040C814: and esi, FFFFFFFEh
  loc_0040C817: push esi
  loc_0040C818: mov Me, esi
  loc_0040C81B: mov ecx, [esi]
  loc_0040C81D: call [ecx+00000004h]
  loc_0040C820: mov edx, [esi]
  loc_0040C822: xor eax, eax
  loc_0040C824: push esi
  loc_0040C825: mov var_18, eax
  loc_0040C828: mov var_1C, eax
  loc_0040C82B: mov var_20, eax
  loc_0040C82E: mov var_24, eax
  loc_0040C831: call [edx+0000032Ch]
  loc_0040C837: mov ebx, [00401080h] ; __vbaObjSet
  loc_0040C83D: push eax
  loc_0040C83E: lea eax, var_24
  loc_0040C841: push eax
  loc_0040C842: call ebx
  loc_0040C844: mov ecx, [esi]
  loc_0040C846: push esi
  loc_0040C847: mov edi, eax
  loc_0040C849: call [ecx+0000032Ch]
  loc_0040C84F: lea edx, var_20
  loc_0040C852: push eax
  loc_0040C853: push edx
  loc_0040C854: call ebx
  loc_0040C856: mov esi, eax
  loc_0040C858: lea ecx, var_18
  loc_0040C85B: push ecx
  loc_0040C85C: push esi
  loc_0040C85D: mov eax, [esi]
  loc_0040C85F: call [eax+00000050h]
  loc_0040C862: test eax, eax
  loc_0040C864: fnclex
  loc_0040C866: jge 0040C877h
  loc_0040C868: push 00000050h
  loc_0040C86A: push 0040575Ch
  loc_0040C86F: push esi
  loc_0040C870: push eax
  loc_0040C871: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040C877: mov edx, var_18
  loc_0040C87A: mov esi, [edi]
  loc_0040C87C: push edx
  loc_0040C87D: push 00405AB4h ; "."
  loc_0040C882: call [00401050h] ; __vbaStrCat
  loc_0040C888: mov edx, eax
  loc_0040C88A: lea ecx, var_1C
  loc_0040C88D: call [004011D0h] ; __vbaStrMove
  loc_0040C893: push eax
  loc_0040C894: push edi
  loc_0040C895: call [esi+00000054h]
  loc_0040C898: test eax, eax
  loc_0040C89A: fnclex
  loc_0040C89C: jge 0040C8ADh
  loc_0040C89E: push 00000054h
  loc_0040C8A0: push 0040575Ch
  loc_0040C8A5: push edi
  loc_0040C8A6: push eax
  loc_0040C8A7: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040C8AD: lea eax, var_1C
  loc_0040C8B0: lea ecx, var_18
  loc_0040C8B3: push eax
  loc_0040C8B4: push ecx
  loc_0040C8B5: push 00000002h
  loc_0040C8B7: call [00401180h] ; __vbaFreeStrList
  loc_0040C8BD: lea edx, var_24
  loc_0040C8C0: lea eax, var_20
  loc_0040C8C3: push edx
  loc_0040C8C4: push eax
  loc_0040C8C5: push 00000002h
  loc_0040C8C7: call [00401040h] ; __vbaFreeObjList
  loc_0040C8CD: add esp, 00000018h
  loc_0040C8D0: call [004010A0h] ; rtcDoEvents
  loc_0040C8D6: mov var_4, 00000000h
  loc_0040C8DD: push 0040C909h
  loc_0040C8E2: jmp 0040C908h
  loc_0040C8E4: lea ecx, var_1C
  loc_0040C8E7: lea edx, var_18
  loc_0040C8EA: push ecx
  loc_0040C8EB: push edx
  loc_0040C8EC: push 00000002h
  loc_0040C8EE: call [00401180h] ; __vbaFreeStrList
  loc_0040C8F4: lea eax, var_24
  loc_0040C8F7: lea ecx, var_20
  loc_0040C8FA: push eax
  loc_0040C8FB: push ecx
  loc_0040C8FC: push 00000002h
  loc_0040C8FE: call [00401040h] ; __vbaFreeObjList
  loc_0040C904: add esp, 00000018h
  loc_0040C907: ret
  loc_0040C908: ret
  loc_0040C909: mov eax, Me
  loc_0040C90C: push eax
  loc_0040C90D: mov edx, [eax]
  loc_0040C90F: call [edx+00000008h]
  loc_0040C912: mov eax, var_4
  loc_0040C915: mov ecx, var_14
  loc_0040C918: pop edi
  loc_0040C919: pop esi
  loc_0040C91A: mov fs:[00000000h], ecx
  loc_0040C921: pop ebx
  loc_0040C922: mov esp, ebp
  loc_0040C924: pop ebp
  loc_0040C925: retn 0004h
End Sub

Private Sub chkSuppressDebug_Click() '40AD40
  loc_0040AD40: push ebp
  loc_0040AD41: mov ebp, esp
  loc_0040AD43: sub esp, 0000000Ch
  loc_0040AD46: push 00401AA6h ; __vbaExceptHandler
  loc_0040AD4B: mov eax, fs:[00000000h]
  loc_0040AD51: push eax
  loc_0040AD52: mov fs:[00000000h], esp
  loc_0040AD59: sub esp, 0000001Ch
  loc_0040AD5C: push ebx
  loc_0040AD5D: push esi
  loc_0040AD5E: push edi
  loc_0040AD5F: mov var_C, esp
  loc_0040AD62: mov var_8, 00401200h
  loc_0040AD69: mov esi, Me
  loc_0040AD6C: mov eax, esi
  loc_0040AD6E: and eax, 00000001h
  loc_0040AD71: mov var_4, eax
  loc_0040AD74: and esi, FFFFFFFEh
  loc_0040AD77: push esi
  loc_0040AD78: mov Me, esi
  loc_0040AD7B: mov ecx, [esi]
  loc_0040AD7D: call [ecx+00000004h]
  loc_0040AD80: mov edx, [esi]
  loc_0040AD82: xor edi, edi
  loc_0040AD84: push esi
  loc_0040AD85: mov var_18, edi
  loc_0040AD88: mov var_1C, edi
  loc_0040AD8B: call [edx+000002FCh]
  loc_0040AD91: push eax
  loc_0040AD92: lea eax, var_18
  loc_0040AD95: push eax
  loc_0040AD96: call [00401080h] ; __vbaObjSet
  loc_0040AD9C: mov esi, eax
  loc_0040AD9E: lea edx, var_1C
  loc_0040ADA1: push edx
  loc_0040ADA2: push esi
  loc_0040ADA3: mov ecx, [esi]
  loc_0040ADA5: call [ecx+000000E0h]
  loc_0040ADAB: cmp eax, edi
  loc_0040ADAD: fnclex
  loc_0040ADAF: jge 0040ADC3h
  loc_0040ADB1: push 000000E0h
  loc_0040ADB6: push 00405354h
  loc_0040ADBB: push esi
  loc_0040ADBC: push eax
  loc_0040ADBD: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040ADC3: xor eax, eax
  loc_0040ADC5: cmp var_1C, 0001h
  loc_0040ADCA: lea ecx, var_18
  loc_0040ADCD: setz al
  loc_0040ADD0: neg eax
  loc_0040ADD2: mov esi, eax
  loc_0040ADD4: call [004011F0h] ; __vbaFreeObj
  loc_0040ADDA: neg si
  loc_0040ADDD: sbb esi, esi
  loc_0040ADDF: mov [00423034h], si
  loc_0040ADE6: mov var_4, edi
  loc_0040ADE9: push 0040ADFBh
  loc_0040ADEE: jmp 0040ADFAh
  loc_0040ADF0: lea ecx, var_18
  loc_0040ADF3: call [004011F0h] ; __vbaFreeObj
  loc_0040ADF9: ret
  loc_0040ADFA: ret
  loc_0040ADFB: mov eax, Me
  loc_0040ADFE: push eax
  loc_0040ADFF: mov ecx, [eax]
  loc_0040AE01: call [ecx+00000008h]
  loc_0040AE04: mov eax, var_4
  loc_0040AE07: mov ecx, var_14
  loc_0040AE0A: pop edi
  loc_0040AE0B: pop esi
  loc_0040AE0C: mov fs:[00000000h], ecx
  loc_0040AE13: pop ebx
  loc_0040AE14: mov esp, ebp
  loc_0040AE16: pop ebp
  loc_0040AE17: retn 0004h
End Sub

Public Function OrphanFileMsg(arg_C) '40C930
  loc_0040C930: push ebp
  loc_0040C931: mov ebp, esp
  loc_0040C933: sub esp, 0000000Ch
  loc_0040C936: push 00401AA6h ; __vbaExceptHandler
  loc_0040C93B: mov eax, fs:[00000000h]
  loc_0040C941: push eax
  loc_0040C942: mov fs:[00000000h], esp
  loc_0040C949: sub esp, 00000070h
  loc_0040C94C: push ebx
  loc_0040C94D: push esi
  loc_0040C94E: push edi
  loc_0040C94F: mov var_C, esp
  loc_0040C952: mov var_8, 00401278h
  loc_0040C959: xor edi, edi
  loc_0040C95B: mov var_4, edi
  loc_0040C95E: mov eax, Me
  loc_0040C961: push eax
  loc_0040C962: mov ecx, [eax]
  loc_0040C964: call [ecx+00000004h]
  loc_0040C967: mov edx, arg_C
  loc_0040C96A: lea ecx, var_20
  loc_0040C96D: mov var_18, edi
  loc_0040C970: mov var_1C, edi
  loc_0040C973: mov [edx], edi
  loc_0040C975: xor edx, edx
  loc_0040C977: mov var_20, edi
  loc_0040C97A: mov var_24, edi
  loc_0040C97D: mov var_28, edi
  loc_0040C980: mov var_38, edi
  loc_0040C983: mov var_48, edi
  loc_0040C986: mov var_58, edi
  loc_0040C989: mov var_68, edi
  loc_0040C98C: mov var_78, edi
  loc_0040C98F: call [00401178h] ; __vbaStrCopy
  loc_0040C995: lea edx, var_78
  loc_0040C998: lea ecx, var_38
  loc_0040C99B: mov var_70, 00405DCCh ; "C:\ProbeData\Complete*.txt"
  loc_0040C9A2: mov var_78, 00000008h
  loc_0040C9A9: call [004011B4h] ; __vbaVarDup
  loc_0040C9AF: lea eax, var_38
  loc_0040C9B2: push edi
  loc_0040C9B3: push eax
  loc_0040C9B4: call [00401150h] ; rtcDir
  loc_0040C9BA: mov esi, [004011D0h] ; __vbaStrMove
  loc_0040C9C0: mov edx, eax
  loc_0040C9C2: lea ecx, var_18
  loc_0040C9C5: call __vbaStrMove
  loc_0040C9C7: lea ecx, var_38
  loc_0040C9CA: call [00401020h] ; __vbaFreeVar
  loc_0040C9D0: mov ebx, [00401050h] ; __vbaStrCat
  loc_0040C9D6: mov ecx, var_18
  loc_0040C9D9: push ecx
  loc_0040C9DA: push edi
  loc_0040C9DB: call [004010DCh] ; __vbaStrCmp
  loc_0040C9E1: test eax, eax
  loc_0040C9E3: jz 0040CAB8h
  loc_0040C9E9: mov edx, var_18
  loc_0040C9EC: push 00405E08h ; "C:\ProbeData\"
  loc_0040C9F1: push edx
  loc_0040C9F2: call ebx
  loc_0040C9F4: mov edx, eax
  loc_0040C9F6: lea ecx, var_24
  loc_0040C9F9: call __vbaStrMove
  loc_0040C9FB: push eax
  loc_0040C9FC: lea eax, var_38
  loc_0040C9FF: push eax
  loc_0040CA00: call [00401188h] ; rtcFileDateTime
  loc_0040CA06: lea ecx, var_48
  loc_0040CA09: push ecx
  loc_0040CA0A: call [004011E4h] ; rtcGetPresentDate
  loc_0040CA10: lea edx, var_48
  loc_0040CA13: lea eax, var_58
  loc_0040CA16: push edx
  loc_0040CA17: push BFF00000h
  loc_0040CA1C: push edi
  loc_0040CA1D: push 00405E28h ; "h"
  loc_0040CA22: push eax
  loc_0040CA23: call [00401058h] ; rtcDateAdd
  loc_0040CA29: lea ecx, var_38
  loc_0040CA2C: lea edx, var_58
  loc_0040CA2F: push ecx
  loc_0040CA30: push edx
  loc_0040CA31: call [004010B0h] ; __vbaVarTstLt
  loc_0040CA37: lea ecx, var_24
  loc_0040CA3A: mov edi, eax
  loc_0040CA3C: call [004011F4h] ; __vbaFreeStr
  loc_0040CA42: lea eax, var_58
  loc_0040CA45: lea ecx, var_38
  loc_0040CA48: push eax
  loc_0040CA49: lea edx, var_48
  loc_0040CA4C: push ecx
  loc_0040CA4D: push edx
  loc_0040CA4E: push 00000003h
  loc_0040CA50: call [00401038h] ; __vbaFreeVarList
  loc_0040CA56: add esp, 00000010h
  loc_0040CA59: test di, di
  loc_0040CA5C: jz 0040CA87h
  loc_0040CA5E: mov eax, var_20
  loc_0040CA61: push eax
  loc_0040CA62: push 004054D8h ; vbCrLf
  loc_0040CA67: call ebx
  loc_0040CA69: mov edx, eax
  loc_0040CA6B: lea ecx, var_24
  loc_0040CA6E: call __vbaStrMove
  loc_0040CA70: mov ecx, var_18
  loc_0040CA73: push eax
  loc_0040CA74: push ecx
  loc_0040CA75: call ebx
  loc_0040CA77: mov edx, eax
  loc_0040CA79: lea ecx, var_20
  loc_0040CA7C: call __vbaStrMove
  loc_0040CA7E: lea ecx, var_24
  loc_0040CA81: call [004011F4h] ; __vbaFreeStr
  loc_0040CA87: lea edx, var_38
  loc_0040CA8A: push 00000000h
  loc_0040CA8C: push edx
  loc_0040CA8D: mov var_30, 80020004h
  loc_0040CA94: mov var_38, 0000000Ah
  loc_0040CA9B: call [00401150h] ; rtcDir
  loc_0040CAA1: mov edx, eax
  loc_0040CAA3: lea ecx, var_18
  loc_0040CAA6: call __vbaStrMove
  loc_0040CAA8: lea ecx, var_38
  loc_0040CAAB: call [00401020h] ; __vbaFreeVar
  loc_0040CAB1: xor edi, edi
  loc_0040CAB3: jmp 0040C9D6h
  loc_0040CAB8: mov eax, var_20
  loc_0040CABB: push eax
  loc_0040CABC: push edi
  loc_0040CABD: call [004010DCh] ; __vbaStrCmp
  loc_0040CAC3: test eax, eax
  loc_0040CAC5: jz 0040CB0Ah
  loc_0040CAC7: push 00405E30h ; "Data files found in C:\ProbeData that have not been collected into the database."
  loc_0040CACC: push 004054D8h ; vbCrLf
  loc_0040CAD1: call ebx
  loc_0040CAD3: mov edx, eax
  loc_0040CAD5: lea ecx, var_24
  loc_0040CAD8: call __vbaStrMove
  loc_0040CADA: push eax
  loc_0040CADB: push 00405ED8h ; "You may continue probing, but please tell an engineer or the programmer!"
  loc_0040CAE0: call ebx
  loc_0040CAE2: mov edx, eax
  loc_0040CAE4: lea ecx, var_28
  loc_0040CAE7: call __vbaStrMove
  loc_0040CAE9: mov ecx, var_20
  loc_0040CAEC: push eax
  loc_0040CAED: push ecx
  loc_0040CAEE: call ebx
  loc_0040CAF0: mov edx, eax
  loc_0040CAF2: lea ecx, var_20
  loc_0040CAF5: call __vbaStrMove
  loc_0040CAF7: lea edx, var_28
  loc_0040CAFA: lea eax, var_24
  loc_0040CAFD: push edx
  loc_0040CAFE: push eax
  loc_0040CAFF: push 00000002h
  loc_0040CB01: call [00401180h] ; __vbaFreeStrList
  loc_0040CB07: add esp, 0000000Ch
  loc_0040CB0A: mov edx, var_20
  loc_0040CB0D: lea ecx, var_1C
  loc_0040CB10: call [00401178h] ; __vbaStrCopy
  loc_0040CB16: fwait
  loc_0040CB17: push 0040CB6Ah
  loc_0040CB1C: jmp 0040CB59h
  loc_0040CB1E: test var_4, 04h
  loc_0040CB22: jz 0040CB2Dh
  loc_0040CB24: lea ecx, var_1C
  loc_0040CB27: call [004011F4h] ; __vbaFreeStr
  loc_0040CB2D: lea ecx, var_28
  loc_0040CB30: lea edx, var_24
  loc_0040CB33: push ecx
  loc_0040CB34: push edx
  loc_0040CB35: push 00000002h
  loc_0040CB37: call [00401180h] ; __vbaFreeStrList
  loc_0040CB3D: lea eax, var_68
  loc_0040CB40: lea ecx, var_58
  loc_0040CB43: push eax
  loc_0040CB44: lea edx, var_48
  loc_0040CB47: push ecx
  loc_0040CB48: lea eax, var_38
  loc_0040CB4B: push edx
  loc_0040CB4C: push eax
  loc_0040CB4D: push 00000004h
  loc_0040CB4F: call [00401038h] ; __vbaFreeVarList
  loc_0040CB55: add esp, 00000020h
  loc_0040CB58: ret
  loc_0040CB59: mov esi, [004011F4h] ; __vbaFreeStr
  loc_0040CB5F: lea ecx, var_18
  loc_0040CB62: call __vbaFreeStr
  loc_0040CB64: lea ecx, var_20
  loc_0040CB67: call __vbaFreeStr
  loc_0040CB69: ret
  loc_0040CB6A: mov eax, Me
  loc_0040CB6D: push eax
  loc_0040CB6E: mov ecx, [eax]
  loc_0040CB70: call [ecx+00000008h]
  loc_0040CB73: mov edx, arg_C
  loc_0040CB76: mov eax, var_1C
  loc_0040CB79: mov [edx], eax
  loc_0040CB7B: mov eax, var_4
  loc_0040CB7E: mov ecx, var_14
  loc_0040CB81: pop edi
  loc_0040CB82: pop esi
  loc_0040CB83: mov fs:[00000000h], ecx
  loc_0040CB8A: pop ebx
  loc_0040CB8B: mov esp, ebp
  loc_0040CB8D: pop ebp
  loc_0040CB8E: retn 0008h
End Function

Private Sub Proc_0_9_40C0A0(arg_C) '40C0A0
  loc_0040C0A0: push ebp
  loc_0040C0A1: mov ebp, esp
  loc_0040C0A3: sub esp, 00000008h
  loc_0040C0A6: push 00401AA6h ; __vbaExceptHandler
  loc_0040C0AB: mov eax, fs:[00000000h]
  loc_0040C0B1: push eax
  loc_0040C0B2: mov fs:[00000000h], esp
  loc_0040C0B9: sub esp, 00000068h
  loc_0040C0BC: push ebx
  loc_0040C0BD: push esi
  loc_0040C0BE: push edi
  loc_0040C0BF: mov var_8, esp
  loc_0040C0C2: mov var_4, 00401230h
  loc_0040C0C9: mov eax, arg_C
  loc_0040C0CC: xor edi, edi
  loc_0040C0CE: mov var_14, edi
  loc_0040C0D1: mov var_18, edi
  loc_0040C0D4: mov eax, [eax]
  loc_0040C0D6: mov var_1C, edi
  loc_0040C0D9: cmp eax, edi
  loc_0040C0DB: mov var_20, edi
  loc_0040C0DE: mov var_24, edi
  loc_0040C0E1: mov var_28, edi
  loc_0040C0E4: mov var_38, edi
  loc_0040C0E7: mov var_48, edi
  loc_0040C0EA: mov var_64, edi
  loc_0040C0ED: mov var_68, edi
  loc_0040C0F0: jle 0040C11Ch
  loc_0040C0F2: cmp eax, 00000002h
  loc_0040C0F5: jle 0040C10Ch
  loc_0040C0F7: cmp eax, 00000003h
  loc_0040C0FA: jnz 0040C11Ch
  loc_0040C0FC: mov edx, 00405B3Ch ; "Manual"
  loc_0040C101: lea ecx, var_18
  loc_0040C104: call [00401178h] ; __vbaStrCopy
  loc_0040C10A: jmp 0040C122h
  loc_0040C10C: mov edx, 00405B2Ch ; "Full"
  loc_0040C111: lea ecx, var_18
  loc_0040C114: call [00401178h] ; __vbaStrCopy
  loc_0040C11A: jmp 0040C122h
  loc_0040C11C: call [0040114Ch] ; __vbaStopExe
  loc_0040C122: mov esi, Me
  loc_0040C125: lea edx, var_28
  loc_0040C128: push edx
  loc_0040C129: push esi
  loc_0040C12A: mov ecx, [esi]
  loc_0040C12C: call [ecx+00000218h]
  loc_0040C132: cmp eax, edi
  loc_0040C134: fnclex
  loc_0040C136: jge 0040C14Eh
  loc_0040C138: push 00000218h
  loc_0040C13D: push 00405120h
  loc_0040C142: push esi
  loc_0040C143: mov esi, [0040105Ch] ; __vbaHresultCheckObj
  loc_0040C149: push eax
  loc_0040C14A: call __vbaHresultCheckObj
  loc_0040C14C: jmp 0040C154h
  loc_0040C14E: mov esi, [0040105Ch] ; __vbaHresultCheckObj
  loc_0040C154: mov eax, var_28
  loc_0040C157: mov var_28, edi
  loc_0040C15A: push eax
  loc_0040C15B: lea eax, var_64
  loc_0040C15E: push eax
  loc_0040C15F: call [00401080h] ; __vbaObjSet
  loc_0040C165: lea ecx, var_14
  loc_0040C168: push eax
  loc_0040C169: lea edx, var_68
  loc_0040C16C: push ecx
  loc_0040C16D: push edx
  loc_0040C16E: push 00405B4Ch
  loc_0040C173: call [00401078h] ; __vbaForEachCollObj
  loc_0040C179: mov edi, var_3C
  loc_0040C17C: mov ebx, var_44
  loc_0040C17F: test eax, eax
  loc_0040C181: jz 0040C30Ah
  loc_0040C187: push 00402208h
  loc_0040C18C: call [00401110h] ; __vbaNew
  loc_0040C192: push eax
  loc_0040C193: lea eax, var_1C
  loc_0040C196: push eax
  loc_0040C197: call [00401080h] ; __vbaObjSet
  loc_0040C19D: mov ecx, var_14
  loc_0040C1A0: push 00000000h
  loc_0040C1A2: push 00405C34h ; "Tag"
  loc_0040C1A7: lea edx, var_38
  loc_0040C1AA: push ecx
  loc_0040C1AB: push edx
  loc_0040C1AC: call [004011C8h] ; __vbaLateMemCallLd
  loc_0040C1B2: add esp, 00000010h
  loc_0040C1B5: push eax
  loc_0040C1B6: call [00401030h] ; __vbaStrVarMove
  loc_0040C1BC: mov edx, eax
  loc_0040C1BE: lea ecx, var_20
  loc_0040C1C1: call [004011D0h] ; __vbaStrMove
  loc_0040C1C7: mov eax, var_1C
  loc_0040C1CA: lea edx, var_20
  loc_0040C1CD: push edx
  loc_0040C1CE: push eax
  loc_0040C1CF: mov ecx, [eax]
  loc_0040C1D1: call [ecx+00000038h]
  loc_0040C1D4: test eax, eax
  loc_0040C1D6: fnclex
  loc_0040C1D8: jge 0040C1E8h
  loc_0040C1DA: mov ecx, var_1C
  loc_0040C1DD: push 00000038h
  loc_0040C1DF: push 00405B8Ch
  loc_0040C1E4: push ecx
  loc_0040C1E5: push eax
  loc_0040C1E6: call __vbaHresultCheckObj
  loc_0040C1E8: lea ecx, var_20
  loc_0040C1EB: call [004011F4h] ; __vbaFreeStr
  loc_0040C1F1: lea ecx, var_38
  loc_0040C1F4: call [00401020h] ; __vbaFreeVar
  loc_0040C1FA: mov eax, var_1C
  loc_0040C1FD: lea ecx, var_20
  loc_0040C200: push ecx
  loc_0040C201: push eax
  loc_0040C202: mov edx, [eax]
  loc_0040C204: call [edx+0000003Ch]
  loc_0040C207: test eax, eax
  loc_0040C209: fnclex
  loc_0040C20B: jge 0040C21Bh
  loc_0040C20D: mov edx, var_1C
  loc_0040C210: push 0000003Ch
  loc_0040C212: push 00405B8Ch
  loc_0040C217: push edx
  loc_0040C218: push eax
  loc_0040C219: call __vbaHresultCheckObj
  loc_0040C21B: mov eax, var_20
  loc_0040C21E: push eax
  loc_0040C21F: push 00000000h
  loc_0040C221: call [004010DCh] ; __vbaStrCmp
  loc_0040C227: mov esi, eax
  loc_0040C229: lea ecx, var_20
  loc_0040C22C: neg esi
  loc_0040C22E: sbb esi, esi
  loc_0040C230: neg esi
  loc_0040C232: neg esi
  loc_0040C234: call [004011F4h] ; __vbaFreeStr
  loc_0040C23A: test si, si
  loc_0040C23D: jz 0040C2D4h
  loc_0040C243: mov edx, 00405C40h ; "View"
  loc_0040C248: lea ecx, var_20
  loc_0040C24B: call [00401178h] ; __vbaStrCopy
  loc_0040C251: mov eax, var_1C
  loc_0040C254: lea edx, var_24
  loc_0040C257: push edx
  loc_0040C258: lea edx, var_20
  loc_0040C25B: mov ecx, [eax]
  loc_0040C25D: push edx
  loc_0040C25E: push eax
  loc_0040C25F: call [ecx+0000002Ch]
  loc_0040C262: test eax, eax
  loc_0040C264: fnclex
  loc_0040C266: jge 0040C27Ah
  loc_0040C268: mov ecx, var_1C
  loc_0040C26B: push 0000002Ch
  loc_0040C26D: push 00405B8Ch
  loc_0040C272: push ecx
  loc_0040C273: push eax
  loc_0040C274: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040C27A: mov edx, var_24
  loc_0040C27D: mov eax, var_18
  loc_0040C280: push edx
  loc_0040C281: push eax
  loc_0040C282: call [004010DCh] ; __vbaStrCmp
  loc_0040C288: mov esi, eax
  loc_0040C28A: lea ecx, var_24
  loc_0040C28D: neg esi
  loc_0040C28F: sbb esi, esi
  loc_0040C291: lea edx, var_20
  loc_0040C294: push ecx
  loc_0040C295: inc esi
  loc_0040C296: push edx
  loc_0040C297: push 00000002h
  loc_0040C299: neg esi
  loc_0040C29B: call [00401180h] ; __vbaFreeStrList
  loc_0040C2A1: add esp, 0000000Ch
  loc_0040C2A4: test si, si
  loc_0040C2A7: jz 0040C2AEh
  loc_0040C2A9: or eax, FFFFFFFFh
  loc_0040C2AC: jmp 0040C2B0h
  loc_0040C2AE: xor eax, eax
  loc_0040C2B0: sub esp, 00000010h
  loc_0040C2B3: mov ecx, 0000000Bh
  loc_0040C2B8: mov edx, esp
  loc_0040C2BA: push 00405C4Ch ; "Visible"
  loc_0040C2BF: mov [edx], ecx
  loc_0040C2C1: mov [edx+00000004h], ebx
  loc_0040C2C4: mov [edx+00000008h], eax
  loc_0040C2C7: mov eax, var_14
  loc_0040C2CA: push eax
  loc_0040C2CB: mov [edx+0000000Ch], edi
  loc_0040C2CE: call [00401068h] ; __vbaLateMemSt
  loc_0040C2D4: push 00405B8Ch
  loc_0040C2D9: push 00000000h
  loc_0040C2DB: call [004011D4h] ; __vbaCastObj
  loc_0040C2E1: lea ecx, var_1C
  loc_0040C2E4: push eax
  loc_0040C2E5: push ecx
  loc_0040C2E6: call [00401080h] ; __vbaObjSet
  loc_0040C2EC: lea edx, var_14
  loc_0040C2EF: lea eax, var_68
  loc_0040C2F2: push edx
  loc_0040C2F3: push eax
  loc_0040C2F4: push 00405B4Ch
  loc_0040C2F9: call [004010C0h] ; __vbaNextEachCollObj
  loc_0040C2FF: mov esi, [0040105Ch] ; __vbaHresultCheckObj
  loc_0040C305: jmp 0040C17Fh
  loc_0040C30A: push 0040C364h
  loc_0040C30F: jmp 0040C337h
  loc_0040C311: lea ecx, var_24
  loc_0040C314: lea edx, var_20
  loc_0040C317: push ecx
  loc_0040C318: push edx
  loc_0040C319: push 00000002h
  loc_0040C31B: call [00401180h] ; __vbaFreeStrList
  loc_0040C321: add esp, 0000000Ch
  loc_0040C324: lea ecx, var_28
  loc_0040C327: call [004011F0h] ; __vbaFreeObj
  loc_0040C32D: lea ecx, var_38
  loc_0040C330: call [00401020h] ; __vbaFreeVar
  loc_0040C336: ret
  loc_0040C337: lea eax, var_68
  loc_0040C33A: lea ecx, var_64
  loc_0040C33D: push eax
  loc_0040C33E: push ecx
  loc_0040C33F: push 00000002h
  loc_0040C341: call [00401040h] ; __vbaFreeObjList
  loc_0040C347: mov esi, [004011F0h] ; __vbaFreeObj
  loc_0040C34D: add esp, 0000000Ch
  loc_0040C350: lea ecx, var_14
  loc_0040C353: call __vbaFreeObj
  loc_0040C355: lea ecx, var_18
  loc_0040C358: call [004011F4h] ; __vbaFreeStr
  loc_0040C35E: lea ecx, var_1C
  loc_0040C361: call __vbaFreeObj
  loc_0040C363: ret
  loc_0040C364: mov ecx, var_10
  loc_0040C367: pop edi
  loc_0040C368: pop esi
  loc_0040C369: xor eax, eax
  loc_0040C36B: mov fs:[00000000h], ecx
  loc_0040C372: pop ebx
  loc_0040C373: mov esp, ebp
  loc_0040C375: pop ebp
  loc_0040C376: retn 0008h
End Sub

Private Sub Proc_0_10_40C480() '40C480
  loc_0040C480: push ecx
  loc_0040C481: mov eax, [esp+00000008h]
  loc_0040C485: lea edx, [esp]
  loc_0040C489: push edx
  loc_0040C48A: push eax
  loc_0040C48B: mov ecx, [eax]
  loc_0040C48D: mov [esp+00000008h], 00000003h
  loc_0040C495: call [ecx+00000708h]
  loc_0040C49B: xor eax, eax
  loc_0040C49D: pop ecx
  loc_0040C49E: retn 0004h
End Sub
