VERSION 5.00
Object = "{00D8E2DC-2077-0149-8120-0049120E3D80}##0"; "AGT3494A.OCX"
Begin VB.Form frmRunTime
  Caption = "LampElectrical Run Time"
  ScaleMode = 1
  AutoRedraw = False
  FontTransparent = True
  Icon = "frmRunTime.frx":0000
  LinkTopic = "Form1"
  ClientLeft = 165
  ClientTop = 450
  ClientWidth = 11625
  ClientHeight = 9795
  StartUpPosition = 3 'Windows Default
  Begin VB.CheckBox chkFlush
    Caption = "Cache the data for later 'Flush'"
    Left = 120
    Top = 1800
    Width = 1575
    Height = 615
    TabIndex = 32
  End
  Begin VB.Frame Frame2
    Caption = "Switch Powering"
    Left = 4080
    Top = 4200
    Width = 5415
    Height = 3135
    TabIndex = 16
    Tag = "View=Manual;"
    Begin VB.TextBox txtMeterCurrentLimit
      Left = 3960
      Top = 2280
      Width = 975
      Height = 285
      Text = "MeterCurrentLimit"
      TabIndex = 36
    End
    Begin VB.TextBox txtMeterRange
      Left = 1560
      Top = 2280
      Width = 975
      Height = 285
      Text = "MeterRange"
      TabIndex = 33
    End
    Begin VB.TextBox txtIterations
      Left = 1560
      Top = 1800
      Width = 975
      Height = 285
      Text = "Iterations"
      TabIndex = 31
    End
    Begin VB.TextBox txtAverages
      Left = 1560
      Top = 1440
      Width = 975
      Height = 285
      Text = "Averages"
      TabIndex = 30
    End
    Begin VB.TextBox txtMeterDelay
      Left = 3960
      Top = 1560
      Width = 975
      Height = 285
      Text = "MeterDelay"
      TabIndex = 26
    End
    Begin VB.TextBox txtDelay3
      Left = 3960
      Top = 1200
      Width = 975
      Height = 285
      Text = "Delay3"
      TabIndex = 20
    End
    Begin VB.TextBox txtDelay2
      Left = 3960
      Top = 840
      Width = 975
      Height = 285
      Text = "Delay2"
      TabIndex = 19
    End
    Begin VB.TextBox txtDelay1
      Left = 3960
      Top = 480
      Width = 975
      Height = 285
      Text = "Delay1"
      TabIndex = 18
    End
    Begin VB.ComboBox ComboVoltage
      Left = 960
      Top = 480
      Width = 1095
      Height = 315
      Text = "Voltage"
      TabIndex = 17
    End
    Begin VB.Label Label12
      Caption = "Meter Current Limit "
      Left = 2880
      Top = 2280
      Width = 975
      Height = 495
      TabIndex = 35
      Alignment = 1 'Right Justify
    End
    Begin VB.Label Label11
      Caption = "Meter Range"
      Left = 120
      Top = 2280
      Width = 1335
      Height = 255
      TabIndex = 34
      Alignment = 1 'Right Justify
    End
    Begin VB.Label Label10
      Caption = "Iterations"
      Left = 360
      Top = 1800
      Width = 975
      Height = 255
      TabIndex = 29
      Alignment = 1 'Right Justify
    End
    Begin VB.Label Label9
      Caption = "Averages for Keithley"
      Left = 360
      Top = 1320
      Width = 1095
      Height = 495
      TabIndex = 28
      Alignment = 1 'Right Justify
    End
    Begin VB.Label Label8
      Caption = "Meter Delay (Keithley Param)"
      Left = 2520
      Top = 1560
      Width = 1335
      Height = 615
      TabIndex = 27
      Alignment = 1 'Right Justify
    End
    Begin VB.Label Label7
      Caption = "NOT USED"
      Left = 2520
      Top = 1200
      Width = 1335
      Height = 255
      TabIndex = 25
      Alignment = 1 'Right Justify
    End
    Begin VB.Label Label6
      Caption = "After relay set, pre Ping"
      Left = 2160
      Top = 840
      Width = 1695
      Height = 255
      TabIndex = 24
      Alignment = 1 'Right Justify
    End
    Begin VB.Label Label5
      Caption = "NOT USED"
      Left = 2520
      Top = 480
      Width = 1335
      Height = 255
      TabIndex = 23
      Alignment = 1 'Right Justify
    End
    Begin VB.Label Label3
      Caption = "Delays (mSec)"
      Left = 3720
      Top = 240
      Width = 1215
      Height = 255
      TabIndex = 22
      Alignment = 2 'Center
    End
    Begin VB.Label Label1
      Caption = "Voltage"
      Left = 120
      Top = 480
      Width = 615
      Height = 255
      TabIndex = 21
    End
  End
  Begin VB.CommandButton cmdRevert
    Caption = "Change to Engineering Mode"
    Left = 1800
    Top = 3240
    Width = 1500
    Height = 615
    TabIndex = 2
  End
  Begin VB.Timer Timer1
    Enabled = 0   'False
    Left = 2400
    Top = 0
  End
  Begin VB.CheckBox chkSuppressDebug
    Caption = "Suppress Debug Messages"
    Left = 1800
    Top = 4080
    Width = 2295
    Height = 255
    TabIndex = 7
  End
  Begin VB.TextBox txtData
    Left = 0
    Top = 7680
    Width = 11055
    Height = 1815
    TabIndex = 14
    MultiLine = -1  'True
    TabStop = 0   'False
    Locked = -1  'True
  End
  Begin Agt3494ALib.Agt3494A HPIB_Relay1
    OleObjectBlob = "frmRunTime.frx":0442
    Left = 9600
    Top = 3960
  End
  Begin Agt3494ALib.Agt3494A HPIB_2001X
    OleObjectBlob = "frmRunTime.frx":04A2
    Left = 9600
    Top = 4680
  End
  Begin Agt3494ALib.Agt3494A HPIB_Keithley2400
    OleObjectBlob = "frmRunTime.frx":0502
    Left = 9600
    Top = 5400
  End
  Begin VB.Frame Frame1
    Caption = "Engineering Mode"
    Left = 4080
    Top = 120
    Width = 6975
    Height = 3495
    TabIndex = 6
    Tag = "View=Manual;"
    Begin VB.TextBox txtWaferID
      Left = 1320
      Top = 3000
      Width = 1215
      Height = 285
      Text = "The Wafer ID"
      TabIndex = 5
    End
    Begin VB.CheckBox chkDBSave
      Caption = "Save the session measurements to the database."
      Left = 480
      Top = 1680
      Width = 3855
      Height = 255
      Enabled = 0   'False
      TabIndex = 13
    End
    Begin VB.CommandButton cmdView
      Caption = "View"
      Left = 4680
      Top = 2040
      Width = 1575
      Height = 255
      TabIndex = 4
    End
    Begin VB.ComboBox comboDies
      Left = 4800
      Top = 480
      Width = 2055
      Height = 315
      Text = "ComboDies"
      TabIndex = 12
    End
    Begin VB.OptionButton optNoJump
      Caption = "Prober stage is already at the correct die. No initial jump."
      Left = 480
      Top = 840
      Width = 4455
      Height = 375
      TabIndex = 11
    End
    Begin VB.OptionButton optJumpFromAlign
      Caption = "Make the jump from the align site to the chosen die."
      Left = 480
      Top = 480
      Width = 4335
      Height = 255
      TabIndex = 10
    End
    Begin VB.TextBox txtFileName
      Left = 1320
      Top = 2400
      Width = 5295
      Height = 285
      Text = "Text1"
      TabIndex = 3
    End
    Begin VB.CheckBox chkSaveText
      Caption = "Save a text copy of session measurements in file."
      Left = 480
      Top = 2040
      Width = 4215
      Height = 255
      TabIndex = 8
    End
    Begin VB.Label Label4
      Caption = "Wafer ID"
      Left = 360
      Top = 3000
      Width = 855
      Height = 255
      TabIndex = 15
    End
    Begin VB.Line Line2
      X1 = 240
      Y1 = 1440
      X2 = 6600
      Y2 = 1440
    End
    Begin VB.Label lblFileName
      Caption = "File Name"
      Left = 360
      Top = 2400
      Width = 855
      Height = 255
      TabIndex = 9
    End
  End
  Begin VB.CommandButton cmdGo
    Caption = "GO"
    Left = 1800
    Top = 1800
    Width = 1500
    Height = 615
    TabIndex = 1
  End
  Begin VB.Timer LoadTimer
    Enabled = 0   'False
    Left = 4560
    Top = 120
  End
  Begin VB.Line Line1
    BorderColor = &HFF&
    X1 = 0
    Y1 = 7560
    X2 = 11040
    Y2 = 7560
    BorderWidth = 3
  End
  Begin VB.Label lblInfo
    Caption = "Label1"
    Left = 120
    Top = 240
    Width = 2655
    Height = 615
    TabIndex = 0
  End
End

Attribute VB_Name = "frmRunTime"


Private Sub chkSaveText_Click() '41C4A0
  loc_0041C4A0: push ebp
  loc_0041C4A1: mov ebp, esp
  loc_0041C4A3: sub esp, 0000000Ch
  loc_0041C4A6: push 00401AA6h ; __vbaExceptHandler
  loc_0041C4AB: mov eax, fs:[00000000h]
  loc_0041C4B1: push eax
  loc_0041C4B2: mov fs:[00000000h], esp
  loc_0041C4B9: sub esp, 0000001Ch
  loc_0041C4BC: push ebx
  loc_0041C4BD: push esi
  loc_0041C4BE: push edi
  loc_0041C4BF: mov var_C, esp
  loc_0041C4C2: mov var_8, 004016A0h
  loc_0041C4C9: mov esi, Me
  loc_0041C4CC: mov eax, esi
  loc_0041C4CE: and eax, 00000001h
  loc_0041C4D1: mov var_4, eax
  loc_0041C4D4: and esi, FFFFFFFEh
  loc_0041C4D7: push esi
  loc_0041C4D8: mov Me, esi
  loc_0041C4DB: mov ecx, [esi]
  loc_0041C4DD: call [ecx+00000004h]
  loc_0041C4E0: mov edx, [esi]
  loc_0041C4E2: xor eax, eax
  loc_0041C4E4: push esi
  loc_0041C4E5: mov var_18, eax
  loc_0041C4E8: mov var_1C, eax
  loc_0041C4EB: call [edx+00000380h]
  loc_0041C4F1: mov edi, [00401080h] ; __vbaObjSet
  loc_0041C4F7: push eax
  loc_0041C4F8: lea eax, var_18
  loc_0041C4FB: push eax
  loc_0041C4FC: call edi
  loc_0041C4FE: mov ebx, eax
  loc_0041C500: lea edx, var_1C
  loc_0041C503: push edx
  loc_0041C504: push ebx
  loc_0041C505: mov ecx, [ebx]
  loc_0041C507: call [ecx+000000E0h]
  loc_0041C50D: test eax, eax
  loc_0041C50F: fnclex
  loc_0041C511: jge 0041C525h
  loc_0041C513: push 000000E0h
  loc_0041C518: push 00405354h
  loc_0041C51D: push ebx
  loc_0041C51E: push eax
  loc_0041C51F: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041C525: xor ebx, ebx
  loc_0041C527: cmp var_1C, 0001h
  loc_0041C52C: lea ecx, var_18
  loc_0041C52F: setz bl
  loc_0041C532: neg ebx
  loc_0041C534: call [004011F0h] ; __vbaFreeObj
  loc_0041C53A: mov eax, [esi]
  loc_0041C53C: push esi
  loc_0041C53D: test bx, bx
  loc_0041C540: jz 0041C5EDh
  loc_0041C546: call [eax+0000037Ch]
  loc_0041C54C: lea ecx, var_18
  loc_0041C54F: push eax
  loc_0041C550: push ecx
  loc_0041C551: call edi
  loc_0041C553: mov ebx, eax
  loc_0041C555: push FFFFFFFFh
  loc_0041C557: push ebx
  loc_0041C558: mov edx, [ebx]
  loc_0041C55A: call [edx+0000008Ch]
  loc_0041C560: test eax, eax
  loc_0041C562: fnclex
  loc_0041C564: jge 0041C578h
  loc_0041C566: push 0000008Ch
  loc_0041C56B: push 00405398h
  loc_0041C570: push ebx
  loc_0041C571: push eax
  loc_0041C572: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041C578: lea ecx, var_18
  loc_0041C57B: call [004011F0h] ; __vbaFreeObj
  loc_0041C581: mov eax, [esi]
  loc_0041C583: push esi
  loc_0041C584: call [eax+0000038Ch]
  loc_0041C58A: lea ecx, var_18
  loc_0041C58D: push eax
  loc_0041C58E: push ecx
  loc_0041C58F: call edi
  loc_0041C591: mov ebx, eax
  loc_0041C593: push FFFFFFFFh
  loc_0041C595: push ebx
  loc_0041C596: mov edx, [ebx]
  loc_0041C598: call [edx+0000009Ch]
  loc_0041C59E: test eax, eax
  loc_0041C5A0: fnclex
  loc_0041C5A2: jge 0041C5B6h
  loc_0041C5A4: push 0000009Ch
  loc_0041C5A9: push 0040575Ch
  loc_0041C5AE: push ebx
  loc_0041C5AF: push eax
  loc_0041C5B0: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041C5B6: mov ebx, [004011F0h] ; __vbaFreeObj
  loc_0041C5BC: lea ecx, var_18
  loc_0041C5BF: call ebx
  loc_0041C5C1: mov eax, [esi]
  loc_0041C5C3: push esi
  loc_0041C5C4: call [eax+0000036Ch]
  loc_0041C5CA: lea ecx, var_18
  loc_0041C5CD: push eax
  loc_0041C5CE: push ecx
  loc_0041C5CF: call edi
  loc_0041C5D1: mov esi, eax
  loc_0041C5D3: push FFFFFFFFh
  loc_0041C5D5: push esi
  loc_0041C5D6: mov edx, [esi]
  loc_0041C5D8: call [edx+0000008Ch]
  loc_0041C5DE: test eax, eax
  loc_0041C5E0: fnclex
  loc_0041C5E2: jge 0041C69Dh
  loc_0041C5E8: jmp 0041C68Bh
  loc_0041C5ED: call [eax+0000037Ch]
  loc_0041C5F3: lea ecx, var_18
  loc_0041C5F6: push eax
  loc_0041C5F7: push ecx
  loc_0041C5F8: call edi
  loc_0041C5FA: mov ebx, eax
  loc_0041C5FC: push 00000000h
  loc_0041C5FE: push ebx
  loc_0041C5FF: mov edx, [ebx]
  loc_0041C601: call [edx+0000008Ch]
  loc_0041C607: test eax, eax
  loc_0041C609: fnclex
  loc_0041C60B: jge 0041C61Fh
  loc_0041C60D: push 0000008Ch
  loc_0041C612: push 00405398h
  loc_0041C617: push ebx
  loc_0041C618: push eax
  loc_0041C619: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041C61F: lea ecx, var_18
  loc_0041C622: call [004011F0h] ; __vbaFreeObj
  loc_0041C628: mov eax, [esi]
  loc_0041C62A: push esi
  loc_0041C62B: call [eax+0000038Ch]
  loc_0041C631: lea ecx, var_18
  loc_0041C634: push eax
  loc_0041C635: push ecx
  loc_0041C636: call edi
  loc_0041C638: mov ebx, eax
  loc_0041C63A: push 00000000h
  loc_0041C63C: push ebx
  loc_0041C63D: mov edx, [ebx]
  loc_0041C63F: call [edx+0000009Ch]
  loc_0041C645: test eax, eax
  loc_0041C647: fnclex
  loc_0041C649: jge 0041C65Dh
  loc_0041C64B: push 0000009Ch
  loc_0041C650: push 0040575Ch
  loc_0041C655: push ebx
  loc_0041C656: push eax
  loc_0041C657: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041C65D: mov ebx, [004011F0h] ; __vbaFreeObj
  loc_0041C663: lea ecx, var_18
  loc_0041C666: call ebx
  loc_0041C668: mov eax, [esi]
  loc_0041C66A: push esi
  loc_0041C66B: call [eax+0000036Ch]
  loc_0041C671: lea ecx, var_18
  loc_0041C674: push eax
  loc_0041C675: push ecx
  loc_0041C676: call edi
  loc_0041C678: mov esi, eax
  loc_0041C67A: push 00000000h
  loc_0041C67C: push esi
  loc_0041C67D: mov edx, [esi]
  loc_0041C67F: call [edx+0000008Ch]
  loc_0041C685: test eax, eax
  loc_0041C687: fnclex
  loc_0041C689: jge 0041C69Dh
  loc_0041C68B: push 0000008Ch
  loc_0041C690: push 00406128h
  loc_0041C695: push esi
  loc_0041C696: push eax
  loc_0041C697: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041C69D: lea ecx, var_18
  loc_0041C6A0: call ebx
  loc_0041C6A2: mov var_4, 00000000h
  loc_0041C6A9: push 0041C6BBh
  loc_0041C6AE: jmp 0041C6BAh
  loc_0041C6B0: lea ecx, var_18
  loc_0041C6B3: call [004011F0h] ; __vbaFreeObj
  loc_0041C6B9: ret
  loc_0041C6BA: ret
  loc_0041C6BB: mov eax, Me
  loc_0041C6BE: push eax
  loc_0041C6BF: mov ecx, [eax]
  loc_0041C6C1: call [ecx+00000008h]
  loc_0041C6C4: mov eax, var_4
  loc_0041C6C7: mov ecx, var_14
  loc_0041C6CA: pop edi
  loc_0041C6CB: pop esi
  loc_0041C6CC: mov fs:[00000000h], ecx
  loc_0041C6D3: pop ebx
  loc_0041C6D4: mov esp, ebp
  loc_0041C6D6: pop ebp
  loc_0041C6D7: retn 0004h
End Sub

Private Sub chkSuppressDebug_Click() '41C6E0
  loc_0041C6E0: push ebp
  loc_0041C6E1: mov ebp, esp
  loc_0041C6E3: sub esp, 0000000Ch
  loc_0041C6E6: push 00401AA6h ; __vbaExceptHandler
  loc_0041C6EB: mov eax, fs:[00000000h]
  loc_0041C6F1: push eax
  loc_0041C6F2: mov fs:[00000000h], esp
  loc_0041C6F9: sub esp, 0000001Ch
  loc_0041C6FC: push ebx
  loc_0041C6FD: push esi
  loc_0041C6FE: push edi
  loc_0041C6FF: mov var_C, esp
  loc_0041C702: mov var_8, 004016B0h
  loc_0041C709: mov esi, Me
  loc_0041C70C: mov eax, esi
  loc_0041C70E: and eax, 00000001h
  loc_0041C711: mov var_4, eax
  loc_0041C714: and esi, FFFFFFFEh
  loc_0041C717: push esi
  loc_0041C718: mov Me, esi
  loc_0041C71B: mov ecx, [esi]
  loc_0041C71D: call [ecx+00000004h]
  loc_0041C720: mov edx, [esi]
  loc_0041C722: xor edi, edi
  loc_0041C724: push esi
  loc_0041C725: mov var_18, edi
  loc_0041C728: mov var_1C, edi
  loc_0041C72B: call [edx+00000358h]
  loc_0041C731: push eax
  loc_0041C732: lea eax, var_18
  loc_0041C735: push eax
  loc_0041C736: call [00401080h] ; __vbaObjSet
  loc_0041C73C: mov esi, eax
  loc_0041C73E: lea edx, var_1C
  loc_0041C741: push edx
  loc_0041C742: push esi
  loc_0041C743: mov ecx, [esi]
  loc_0041C745: call [ecx+000000E0h]
  loc_0041C74B: cmp eax, edi
  loc_0041C74D: fnclex
  loc_0041C74F: jge 0041C763h
  loc_0041C751: push 000000E0h
  loc_0041C756: push 00405354h
  loc_0041C75B: push esi
  loc_0041C75C: push eax
  loc_0041C75D: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041C763: xor eax, eax
  loc_0041C765: cmp var_1C, 0001h
  loc_0041C76A: lea ecx, var_18
  loc_0041C76D: setz al
  loc_0041C770: neg eax
  loc_0041C772: mov esi, eax
  loc_0041C774: call [004011F0h] ; __vbaFreeObj
  loc_0041C77A: neg si
  loc_0041C77D: sbb esi, esi
  loc_0041C77F: mov [00423034h], si
  loc_0041C786: mov var_4, edi
  loc_0041C789: push 0041C79Bh
  loc_0041C78E: jmp 0041C79Ah
  loc_0041C790: lea ecx, var_18
  loc_0041C793: call [004011F0h] ; __vbaFreeObj
  loc_0041C799: ret
  loc_0041C79A: ret
  loc_0041C79B: mov eax, Me
  loc_0041C79E: push eax
  loc_0041C79F: mov ecx, [eax]
  loc_0041C7A1: call [ecx+00000008h]
  loc_0041C7A4: mov eax, var_4
  loc_0041C7A7: mov ecx, var_14
  loc_0041C7AA: pop edi
  loc_0041C7AB: pop esi
  loc_0041C7AC: mov fs:[00000000h], ecx
  loc_0041C7B3: pop ebx
  loc_0041C7B4: mov esp, ebp
  loc_0041C7B6: pop ebp
  loc_0041C7B7: retn 0004h
End Sub

Private Sub Timer1_Timer() '41C3E0
  loc_0041C3E0: push ebp
  loc_0041C3E1: mov ebp, esp
  loc_0041C3E3: sub esp, 0000000Ch
  loc_0041C3E6: push 00401AA6h ; __vbaExceptHandler
  loc_0041C3EB: mov eax, fs:[00000000h]
  loc_0041C3F1: push eax
  loc_0041C3F2: mov fs:[00000000h], esp
  loc_0041C3F9: sub esp, 00000014h
  loc_0041C3FC: push ebx
  loc_0041C3FD: push esi
  loc_0041C3FE: push edi
  loc_0041C3FF: mov var_C, esp
  loc_0041C402: mov var_8, 00401690h
  loc_0041C409: mov esi, Me
  loc_0041C40C: mov eax, esi
  loc_0041C40E: and eax, 00000001h
  loc_0041C411: mov var_4, eax
  loc_0041C414: and esi, FFFFFFFEh
  loc_0041C417: push esi
  loc_0041C418: mov Me, esi
  loc_0041C41B: mov ecx, [esi]
  loc_0041C41D: call [ecx+00000004h]
  loc_0041C420: mov edx, [esi]
  loc_0041C422: xor edi, edi
  loc_0041C424: push esi
  loc_0041C425: mov var_18, edi
  loc_0041C428: call [edx+00000354h]
  loc_0041C42E: push eax
  loc_0041C42F: lea eax, var_18
  loc_0041C432: push eax
  loc_0041C433: call [00401080h] ; __vbaObjSet
  loc_0041C439: mov esi, eax
  loc_0041C43B: push edi
  loc_0041C43C: push esi
  loc_0041C43D: mov ecx, [esi]
  loc_0041C43F: call [ecx+0000005Ch]
  loc_0041C442: cmp eax, edi
  loc_0041C444: fnclex
  loc_0041C446: jge 0041C457h
  loc_0041C448: push 0000005Ch
  loc_0041C44A: push 004056F4h
  loc_0041C44F: push esi
  loc_0041C450: push eax
  loc_0041C451: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041C457: lea ecx, var_18
  loc_0041C45A: call [004011F0h] ; __vbaFreeObj
  loc_0041C460: mov [00423030h], FFFFFFh
  loc_0041C469: mov var_4, edi
  loc_0041C46C: push 0041C47Eh
  loc_0041C471: jmp 0041C47Dh
  loc_0041C473: lea ecx, var_18
  loc_0041C476: call [004011F0h] ; __vbaFreeObj
  loc_0041C47C: ret
  loc_0041C47D: ret
  loc_0041C47E: mov eax, Me
  loc_0041C481: push eax
  loc_0041C482: mov edx, [eax]
  loc_0041C484: call [edx+00000008h]
  loc_0041C487: mov eax, var_4
  loc_0041C48A: mov ecx, var_14
  loc_0041C48D: pop edi
  loc_0041C48E: pop esi
  loc_0041C48F: mov fs:[00000000h], ecx
  loc_0041C496: pop ebx
  loc_0041C497: mov esp, ebp
  loc_0041C499: pop ebp
  loc_0041C49A: retn 0004h
End Sub

Private Sub ComboVoltage_LostFocus() '41C7C0
  loc_0041C7C0: push ebp
  loc_0041C7C1: mov ebp, esp
  loc_0041C7C3: sub esp, 0000000Ch
  loc_0041C7C6: push 00401AA6h ; __vbaExceptHandler
  loc_0041C7CB: mov eax, fs:[00000000h]
  loc_0041C7D1: push eax
  loc_0041C7D2: mov fs:[00000000h], esp
  loc_0041C7D9: sub esp, 00000098h
  loc_0041C7DF: push ebx
  loc_0041C7E0: push esi
  loc_0041C7E1: push edi
  loc_0041C7E2: mov var_C, esp
  loc_0041C7E5: mov var_8, 004016C0h
  loc_0041C7EC: mov esi, Me
  loc_0041C7EF: mov eax, esi
  loc_0041C7F1: and eax, 00000001h
  loc_0041C7F4: mov var_4, eax
  loc_0041C7F7: and esi, FFFFFFFEh
  loc_0041C7FA: push esi
  loc_0041C7FB: mov Me, esi
  loc_0041C7FE: mov ecx, [esi]
  loc_0041C800: call [ecx+00000004h]
  loc_0041C803: mov edx, [esi]
  loc_0041C805: xor edi, edi
  loc_0041C807: push esi
  loc_0041C808: mov var_18, edi
  loc_0041C80B: mov var_1C, edi
  loc_0041C80E: mov var_20, edi
  loc_0041C811: mov var_24, edi
  loc_0041C814: mov var_34, edi
  loc_0041C817: mov var_44, edi
  loc_0041C81A: mov var_54, edi
  loc_0041C81D: mov var_64, edi
  loc_0041C820: mov var_74, edi
  loc_0041C823: call [edx+00000324h]
  loc_0041C829: push eax
  loc_0041C82A: lea eax, var_24
  loc_0041C82D: push eax
  loc_0041C82E: call [00401080h] ; __vbaObjSet
  loc_0041C834: mov ebx, eax
  loc_0041C836: lea edx, var_18
  loc_0041C839: push edx
  loc_0041C83A: push ebx
  loc_0041C83B: mov ecx, [ebx]
  loc_0041C83D: call [ecx+000000A8h]
  loc_0041C843: cmp eax, edi
  loc_0041C845: fnclex
  loc_0041C847: jge 0041C85Bh
  loc_0041C849: push 000000A8h
  loc_0041C84E: push 004055DCh
  loc_0041C853: push ebx
  loc_0041C854: push eax
  loc_0041C855: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041C85B: mov eax, var_18
  loc_0041C85E: mov var_18, edi
  loc_0041C861: mov var_2C, eax
  loc_0041C864: lea eax, var_34
  loc_0041C867: push eax
  loc_0041C868: mov var_34, 00000008h
  loc_0041C86F: call [004010E8h] ; rtcIsNumeric
  loc_0041C875: mov bx, ax
  loc_0041C878: lea ecx, var_24
  loc_0041C87B: not ebx
  loc_0041C87D: call [004011F0h] ; __vbaFreeObj
  loc_0041C883: lea ecx, var_34
  loc_0041C886: call [00401020h] ; __vbaFreeVar
  loc_0041C88C: cmp bx, di
  loc_0041C88F: jz 0041C9D4h
  loc_0041C895: mov ecx, [esi]
  loc_0041C897: push esi
  loc_0041C898: call [ecx+00000324h]
  loc_0041C89E: lea edx, var_24
  loc_0041C8A1: push eax
  loc_0041C8A2: push edx
  loc_0041C8A3: call [00401080h] ; __vbaObjSet
  loc_0041C8A9: mov ebx, eax
  loc_0041C8AB: lea ecx, var_18
  loc_0041C8AE: push ecx
  loc_0041C8AF: push ebx
  loc_0041C8B0: mov eax, [ebx]
  loc_0041C8B2: call [eax+000000A8h]
  loc_0041C8B8: cmp eax, edi
  loc_0041C8BA: fnclex
  loc_0041C8BC: jge 0041C8D0h
  loc_0041C8BE: push 000000A8h
  loc_0041C8C3: push 004055DCh
  loc_0041C8C8: push ebx
  loc_0041C8C9: push eax
  loc_0041C8CA: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041C8D0: mov ecx, 80020004h
  loc_0041C8D5: mov eax, 0000000Ah
  loc_0041C8DA: mov var_5C, ecx
  loc_0041C8DD: mov var_4C, ecx
  loc_0041C8E0: lea edx, var_74
  loc_0041C8E3: lea ecx, var_44
  loc_0041C8E6: mov var_64, eax
  loc_0041C8E9: mov var_54, eax
  loc_0041C8EC: mov var_6C, 004050E8h ; "IMT LampElectrical Probing"
  loc_0041C8F3: mov var_74, 00000008h
  loc_0041C8FA: call [004011B4h] ; __vbaVarDup
  loc_0041C900: mov edi, [00401050h] ; __vbaStrCat
  loc_0041C906: push 00407AF0h ; "You cannot enter a non numeric for the drive Voltage!"
  loc_0041C90B: push 004054D8h ; vbCrLf
  loc_0041C910: call edi
  loc_0041C912: mov ebx, [004011D0h] ; __vbaStrMove
  loc_0041C918: mov edx, eax
  loc_0041C91A: lea ecx, var_1C
  loc_0041C91D: call ebx
  loc_0041C91F: mov edx, var_18
  loc_0041C922: push eax
  loc_0041C923: push edx
  loc_0041C924: call edi
  loc_0041C926: mov edx, eax
  loc_0041C928: lea ecx, var_20
  loc_0041C92B: call ebx
  loc_0041C92D: push eax
  loc_0041C92E: push 00407B60h ; " is not a number"
  loc_0041C933: call edi
  loc_0041C935: mov var_2C, eax
  loc_0041C938: lea eax, var_64
  loc_0041C93B: lea ecx, var_54
  loc_0041C93E: push eax
  loc_0041C93F: lea edx, var_44
  loc_0041C942: push ecx
  loc_0041C943: push edx
  loc_0041C944: lea eax, var_34
  loc_0041C947: push 00000010h
  loc_0041C949: push eax
  loc_0041C94A: mov var_34, 00000008h
  loc_0041C951: call [00401084h] ; rtcMsgBox
  loc_0041C957: lea ecx, var_20
  loc_0041C95A: lea edx, var_18
  loc_0041C95D: push ecx
  loc_0041C95E: lea eax, var_1C
  loc_0041C961: push edx
  loc_0041C962: push eax
  loc_0041C963: push 00000003h
  loc_0041C965: call [00401180h] ; __vbaFreeStrList
  loc_0041C96B: mov edi, [004011F0h] ; __vbaFreeObj
  loc_0041C971: add esp, 00000010h
  loc_0041C974: lea ecx, var_24
  loc_0041C977: call edi
  loc_0041C979: lea ecx, var_64
  loc_0041C97C: lea edx, var_54
  loc_0041C97F: push ecx
  loc_0041C980: lea eax, var_44
  loc_0041C983: push edx
  loc_0041C984: lea ecx, var_34
  loc_0041C987: push eax
  loc_0041C988: push ecx
  loc_0041C989: push 00000004h
  loc_0041C98B: call [00401038h] ; __vbaFreeVarList
  loc_0041C991: mov edx, [esi]
  loc_0041C993: add esp, 00000014h
  loc_0041C996: push esi
  loc_0041C997: call [edx+00000324h]
  loc_0041C99D: push eax
  loc_0041C99E: lea eax, var_24
  loc_0041C9A1: push eax
  loc_0041C9A2: call [00401080h] ; __vbaObjSet
  loc_0041C9A8: mov esi, eax
  loc_0041C9AA: push 00000001h
  loc_0041C9AC: push esi
  loc_0041C9AD: mov ecx, [esi]
  loc_0041C9AF: call [ecx+000000F4h]
  loc_0041C9B5: test eax, eax
  loc_0041C9B7: fnclex
  loc_0041C9B9: jge 0041C9CDh
  loc_0041C9BB: push 000000F4h
  loc_0041C9C0: push 004055DCh
  loc_0041C9C5: push esi
  loc_0041C9C6: push eax
  loc_0041C9C7: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041C9CD: lea ecx, var_24
  loc_0041C9D0: call edi
  loc_0041C9D2: xor edi, edi
  loc_0041C9D4: mov var_4, edi
  loc_0041C9D7: push 0041CA1Bh
  loc_0041C9DC: jmp 0041CA1Ah
  loc_0041C9DE: lea edx, var_20
  loc_0041C9E1: lea eax, var_1C
  loc_0041C9E4: push edx
  loc_0041C9E5: lea ecx, var_18
  loc_0041C9E8: push eax
  loc_0041C9E9: push ecx
  loc_0041C9EA: push 00000003h
  loc_0041C9EC: call [00401180h] ; __vbaFreeStrList
  loc_0041C9F2: add esp, 00000010h
  loc_0041C9F5: lea ecx, var_24
  loc_0041C9F8: call [004011F0h] ; __vbaFreeObj
  loc_0041C9FE: lea edx, var_64
  loc_0041CA01: lea eax, var_54
  loc_0041CA04: push edx
  loc_0041CA05: lea ecx, var_44
  loc_0041CA08: push eax
  loc_0041CA09: lea edx, var_34
  loc_0041CA0C: push ecx
  loc_0041CA0D: push edx
  loc_0041CA0E: push 00000004h
  loc_0041CA10: call [00401038h] ; __vbaFreeVarList
  loc_0041CA16: add esp, 00000014h
  loc_0041CA19: ret
  loc_0041CA1A: ret
  loc_0041CA1B: mov eax, Me
  loc_0041CA1E: push eax
  loc_0041CA1F: mov ecx, [eax]
  loc_0041CA21: call [ecx+00000008h]
  loc_0041CA24: mov eax, var_4
  loc_0041CA27: mov ecx, var_14
  loc_0041CA2A: pop edi
  loc_0041CA2B: pop esi
  loc_0041CA2C: mov fs:[00000000h], ecx
  loc_0041CA33: pop ebx
  loc_0041CA34: mov esp, ebp
  loc_0041CA36: pop ebp
  loc_0041CA37: retn 0004h
End Sub

Private Sub cmdRevert_Click() '414AC0
  loc_00414AC0: push ebp
  loc_00414AC1: mov ebp, esp
  loc_00414AC3: sub esp, 0000000Ch
  loc_00414AC6: push 00401AA6h ; __vbaExceptHandler
  loc_00414ACB: mov eax, fs:[00000000h]
  loc_00414AD1: push eax
  loc_00414AD2: mov fs:[00000000h], esp
  loc_00414AD9: sub esp, 0000001Ch
  loc_00414ADC: push ebx
  loc_00414ADD: push esi
  loc_00414ADE: push edi
  loc_00414ADF: mov var_C, esp
  loc_00414AE2: mov var_8, 004012A0h
  loc_00414AE9: mov esi, Me
  loc_00414AEC: mov eax, esi
  loc_00414AEE: and eax, 00000001h
  loc_00414AF1: mov var_4, eax
  loc_00414AF4: and esi, FFFFFFFEh
  loc_00414AF7: push esi
  loc_00414AF8: mov Me, esi
  loc_00414AFB: mov ecx, [esi]
  loc_00414AFD: call [ecx+00000004h]
  loc_00414B00: mov edx, [esi]
  loc_00414B02: xor eax, eax
  loc_00414B04: push esi
  loc_00414B05: mov var_18, eax
  loc_00414B08: mov var_1C, eax
  loc_00414B0B: call [edx+00000350h]
  loc_00414B11: mov ebx, [00401080h] ; __vbaObjSet
  loc_00414B17: push eax
  loc_00414B18: lea eax, var_1C
  loc_00414B1B: push eax
  loc_00414B1C: call ebx
  loc_00414B1E: mov edi, eax
  loc_00414B20: lea edx, var_18
  loc_00414B23: push edx
  loc_00414B24: push edi
  loc_00414B25: mov ecx, [edi]
  loc_00414B27: call [ecx+00000050h]
  loc_00414B2A: test eax, eax
  loc_00414B2C: fnclex
  loc_00414B2E: jge 00414B3Fh
  loc_00414B30: push 00000050h
  loc_00414B32: push 00406128h
  loc_00414B37: push edi
  loc_00414B38: push eax
  loc_00414B39: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00414B3F: mov eax, var_18
  loc_00414B42: push eax
  loc_00414B43: push 00406DCCh ; "Change to Engineering Mode"
  loc_00414B48: call [004010DCh] ; __vbaStrCmp
  loc_00414B4E: mov edi, eax
  loc_00414B50: lea ecx, var_18
  loc_00414B53: neg edi
  loc_00414B55: sbb edi, edi
  loc_00414B57: inc edi
  loc_00414B58: neg edi
  loc_00414B5A: call [004011F4h] ; __vbaFreeStr
  loc_00414B60: lea ecx, var_1C
  loc_00414B63: call [004011F0h] ; __vbaFreeObj
  loc_00414B69: mov ecx, [esi]
  loc_00414B6B: push esi
  loc_00414B6C: test di, di
  loc_00414B6F: jz 00414BB4h
  loc_00414B71: call [ecx+00000350h]
  loc_00414B77: lea edx, var_1C
  loc_00414B7A: push eax
  loc_00414B7B: push edx
  loc_00414B7C: call ebx
  loc_00414B7E: mov edi, eax
  loc_00414B80: push 00406E08h ; "Change to Production Mode"
  loc_00414B85: push edi
  loc_00414B86: mov eax, [edi]
  loc_00414B88: call [eax+00000054h]
  loc_00414B8B: test eax, eax
  loc_00414B8D: fnclex
  loc_00414B8F: jge 00414BA0h
  loc_00414B91: push 00000054h
  loc_00414B93: push 00406128h
  loc_00414B98: push edi
  loc_00414B99: push eax
  loc_00414B9A: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00414BA0: lea ecx, var_1C
  loc_00414BA3: call [004011F0h] ; __vbaFreeObj
  loc_00414BA9: mov [00423032h], 0000h
  loc_00414BB2: jmp 00414BF5h
  loc_00414BB4: call [ecx+00000350h]
  loc_00414BBA: lea edx, var_1C
  loc_00414BBD: push eax
  loc_00414BBE: push edx
  loc_00414BBF: call ebx
  loc_00414BC1: mov edi, eax
  loc_00414BC3: push 00406DCCh ; "Change to Engineering Mode"
  loc_00414BC8: push edi
  loc_00414BC9: mov eax, [edi]
  loc_00414BCB: call [eax+00000054h]
  loc_00414BCE: test eax, eax
  loc_00414BD0: fnclex
  loc_00414BD2: jge 00414BE3h
  loc_00414BD4: push 00000054h
  loc_00414BD6: push 00406128h
  loc_00414BDB: push edi
  loc_00414BDC: push eax
  loc_00414BDD: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00414BE3: lea ecx, var_1C
  loc_00414BE6: call [004011F0h] ; __vbaFreeObj
  loc_00414BEC: mov [00423032h], FFFFFFh
  loc_00414BF5: mov ecx, [esi]
  loc_00414BF7: push esi
  loc_00414BF8: mov [esi+0000005Ch], FFFFFFh
  loc_00414BFE: call [ecx+00000718h]
  loc_00414C04: test eax, eax
  loc_00414C06: jge 00414C1Ah
  loc_00414C08: push 00000718h
  loc_00414C0D: push 0040579Ch ; "#]=VｫoyAｷ ;ﾑs：ﾚLabel12"
  loc_00414C12: push esi
  loc_00414C13: push eax
  loc_00414C14: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00414C1A: mov var_4, 00000000h
  loc_00414C21: push 00414C3Ch
  loc_00414C26: jmp 00414C3Bh
  loc_00414C28: lea ecx, var_18
  loc_00414C2B: call [004011F4h] ; __vbaFreeStr
  loc_00414C31: lea ecx, var_1C
  loc_00414C34: call [004011F0h] ; __vbaFreeObj
  loc_00414C3A: ret
  loc_00414C3B: ret
  loc_00414C3C: mov eax, Me
  loc_00414C3F: push eax
  loc_00414C40: mov edx, [eax]
  loc_00414C42: call [edx+00000008h]
  loc_00414C45: mov eax, var_4
  loc_00414C48: mov ecx, var_14
  loc_00414C4B: pop edi
  loc_00414C4C: pop esi
  loc_00414C4D: mov fs:[00000000h], ecx
  loc_00414C54: pop ebx
  loc_00414C55: mov esp, ebp
  loc_00414C57: pop ebp
  loc_00414C58: retn 0004h
End Sub

Private Sub cmdGo_Click() '40CBA0
  loc_0040CBA0: push ebp
  loc_0040CBA1: mov ebp, esp
  loc_0040CBA3: sub esp, 0000000Ch
  loc_0040CBA6: push 00401AA6h ; __vbaExceptHandler
  loc_0040CBAB: mov eax, fs:[00000000h]
  loc_0040CBB1: push eax
  loc_0040CBB2: mov fs:[00000000h], esp
  loc_0040CBB9: mov eax, 000005E0h
  loc_0040CBBE: call 00401AA0h ; __vbaChkstk
  loc_0040CBC3: push ebx
  loc_0040CBC4: push esi
  loc_0040CBC5: push edi
  loc_0040CBC6: mov var_C, esp
  loc_0040CBC9: mov var_8, 00401290h
  loc_0040CBD0: mov eax, Me
  loc_0040CBD3: and eax, 00000001h
  loc_0040CBD6: mov var_4, eax
  loc_0040CBD9: mov ecx, Me
  loc_0040CBDC: and ecx, FFFFFFFEh
  loc_0040CBDF: mov Me, ecx
  loc_0040CBE2: mov edx, Me
  loc_0040CBE5: mov eax, [edx]
  loc_0040CBE7: mov ecx, Me
  loc_0040CBEA: push ecx
  loc_0040CBEB: call [eax+00000004h]
  loc_0040CBEE: push 00000005h
  loc_0040CBF0: push 00406DB0h
  loc_0040CBF5: lea edx, var_38
  loc_0040CBF8: push edx
  loc_0040CBF9: call [004010E0h] ; __vbaAryConstruct2
  loc_0040CBFF: push 00000005h
  loc_0040CC01: push 00406DB0h
  loc_0040CC06: lea eax, var_B8
  loc_0040CC0C: push eax
  loc_0040CC0D: call [004010E0h] ; __vbaAryConstruct2
  loc_0040CC13: mov ecx, Me
  loc_0040CC16: mov edx, [ecx]
  loc_0040CC18: mov eax, Me
  loc_0040CC1B: push eax
  loc_0040CC1C: call [edx+00000390h]
  loc_0040CC22: push eax
  loc_0040CC23: lea ecx, var_118
  loc_0040CC29: push ecx
  loc_0040CC2A: call [00401080h] ; __vbaObjSet
  loc_0040CC30: mov var_2C0, eax
  loc_0040CC36: lea edx, var_C8
  loc_0040CC3C: push edx
  loc_0040CC3D: mov eax, var_2C0
  loc_0040CC43: mov ecx, [eax]
  loc_0040CC45: mov edx, var_2C0
  loc_0040CC4B: push edx
  loc_0040CC4C: call [ecx+00000050h]
  loc_0040CC4F: fnclex
  loc_0040CC51: mov var_2C4, eax
  loc_0040CC57: cmp var_2C4, 00000000h
  loc_0040CC5E: jge 0040CC83h
  loc_0040CC60: push 00000050h
  loc_0040CC62: push 00406128h
  loc_0040CC67: mov eax, var_2C0
  loc_0040CC6D: push eax
  loc_0040CC6E: mov ecx, var_2C4
  loc_0040CC74: push ecx
  loc_0040CC75: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040CC7B: mov var_374, eax
  loc_0040CC81: jmp 0040CC8Dh
  loc_0040CC83: mov var_374, 00000000h
  loc_0040CC8D: mov edx, var_C8
  loc_0040CC93: mov var_330, edx
  loc_0040CC99: mov var_C8, 00000000h
  loc_0040CCA3: mov eax, var_330
  loc_0040CCA9: mov var_130, eax
  loc_0040CCAF: mov var_138, 00000008h
  loc_0040CCB9: lea ecx, var_138
  loc_0040CCBF: push ecx
  loc_0040CCC0: lea edx, var_148
  loc_0040CCC6: push edx
  loc_0040CCC7: call [004010D4h] ; rtcUpperCaseVar
  loc_0040CCCD: lea edx, var_148
  loc_0040CCD3: lea ecx, var_308
  loc_0040CCD9: call [00401014h] ; __vbaVarMove
  loc_0040CCDF: lea ecx, var_118
  loc_0040CCE5: call [004011F0h] ; __vbaFreeObj
  loc_0040CCEB: lea ecx, var_138
  loc_0040CCF1: call [00401020h] ; __vbaFreeVar
  loc_0040CCF7: mov var_250, 0040613Ch ; "CANCEL"
  loc_0040CD01: mov var_258, 00008008h
  loc_0040CD0B: lea eax, var_308
  loc_0040CD11: push eax
  loc_0040CD12: lea ecx, var_258
  loc_0040CD18: push ecx
  loc_0040CD19: call [004010E4h] ; __vbaVarTstEq
  loc_0040CD1F: movsx edx, ax
  loc_0040CD22: test edx, edx
  loc_0040CD24: jz 0040CD34h
  loc_0040CD26: mov eax, Me
  loc_0040CD29: mov [eax+0000005Eh], FFFFFFh
  loc_0040CD2F: jmp 0041489Fh
  loc_0040CD34: push 00402208h
  loc_0040CD39: call [00401110h] ; __vbaNew
  loc_0040CD3F: push eax
  loc_0040CD40: lea ecx, var_C0
  loc_0040CD46: push ecx
  loc_0040CD47: call [00401080h] ; __vbaObjSet
  loc_0040CD4D: mov edx, Me
  loc_0040CD50: mov edx, [edx+00000038h]
  loc_0040CD53: lea ecx, var_C8
  loc_0040CD59: call [00401178h] ; __vbaStrCopy
  loc_0040CD5F: lea eax, var_C8
  loc_0040CD65: push eax
  loc_0040CD66: mov ecx, var_C0
  loc_0040CD6C: mov edx, [ecx]
  loc_0040CD6E: mov eax, var_C0
  loc_0040CD74: push eax
  loc_0040CD75: call [edx+00000038h]
  loc_0040CD78: fnclex
  loc_0040CD7A: mov var_2C0, eax
  loc_0040CD80: cmp var_2C0, 00000000h
  loc_0040CD87: jge 0040CDACh
  loc_0040CD89: push 00000038h
  loc_0040CD8B: push 00405B8Ch
  loc_0040CD90: mov ecx, var_C0
  loc_0040CD96: push ecx
  loc_0040CD97: mov edx, var_2C0
  loc_0040CD9D: push edx
  loc_0040CD9E: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040CDA4: mov var_378, eax
  loc_0040CDAA: jmp 0040CDB6h
  loc_0040CDAC: mov var_378, 00000000h
  loc_0040CDB6: lea ecx, var_C8
  loc_0040CDBC: call [004011F4h] ; __vbaFreeStr
  loc_0040CDC2: mov eax, Me
  loc_0040CDC5: mov ecx, [eax]
  loc_0040CDC7: mov edx, Me
  loc_0040CDCA: push edx
  loc_0040CDCB: call [ecx+00000364h]
  loc_0040CDD1: push eax
  loc_0040CDD2: lea eax, var_118
  loc_0040CDD8: push eax
  loc_0040CDD9: call [00401080h] ; __vbaObjSet
  loc_0040CDDF: mov var_2C0, eax
  loc_0040CDE5: lea ecx, var_C8
  loc_0040CDEB: push ecx
  loc_0040CDEC: mov edx, var_2C0
  loc_0040CDF2: mov eax, [edx]
  loc_0040CDF4: mov ecx, var_2C0
  loc_0040CDFA: push ecx
  loc_0040CDFB: call [eax+000000A0h]
  loc_0040CE01: fnclex
  loc_0040CE03: mov var_2C4, eax
  loc_0040CE09: cmp var_2C4, 00000000h
  loc_0040CE10: jge 0040CE38h
  loc_0040CE12: push 000000A0h
  loc_0040CE17: push 00405398h
  loc_0040CE1C: mov edx, var_2C0
  loc_0040CE22: push edx
  loc_0040CE23: mov eax, var_2C4
  loc_0040CE29: push eax
  loc_0040CE2A: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040CE30: mov var_37C, eax
  loc_0040CE36: jmp 0040CE42h
  loc_0040CE38: mov var_37C, 00000000h
  loc_0040CE42: mov ecx, var_C8
  loc_0040CE48: push ecx
  loc_0040CE49: push 004053ACh ; "The Wafer ID"
  loc_0040CE4E: call [004010DCh] ; __vbaStrCmp
  loc_0040CE54: neg eax
  loc_0040CE56: sbb eax, eax
  loc_0040CE58: inc eax
  loc_0040CE59: neg eax
  loc_0040CE5B: mov dx, [00423032h]
  loc_0040CE62: not dx
  loc_0040CE65: and ax, dx
  loc_0040CE68: mov var_2C8, ax
  loc_0040CE6F: lea ecx, var_C8
  loc_0040CE75: call [004011F4h] ; __vbaFreeStr
  loc_0040CE7B: lea ecx, var_118
  loc_0040CE81: call [004011F0h] ; __vbaFreeObj
  loc_0040CE87: movsx eax, var_2C8
  loc_0040CE8E: test eax, eax
  loc_0040CE90: jz 0040CF5Ah
  loc_0040CE96: mov var_160, 80020004h
  loc_0040CEA0: mov var_168, 0000000Ah
  loc_0040CEAA: mov var_150, 80020004h
  loc_0040CEB4: mov var_158, 0000000Ah
  loc_0040CEBE: mov var_260, 004050E8h ; "IMT LampElectrical Probing"
  loc_0040CEC8: mov var_268, 00000008h
  loc_0040CED2: lea edx, var_268
  loc_0040CED8: lea ecx, var_148
  loc_0040CEDE: call [004011B4h] ; __vbaVarDup
  loc_0040CEE4: mov var_250, 00406210h ; "Please enter a Wafer ID"
  loc_0040CEEE: mov var_258, 00000008h
  loc_0040CEF8: lea edx, var_258
  loc_0040CEFE: lea ecx, var_138
  loc_0040CF04: call [004011B4h] ; __vbaVarDup
  loc_0040CF0A: lea ecx, var_168
  loc_0040CF10: push ecx
  loc_0040CF11: lea edx, var_158
  loc_0040CF17: push edx
  loc_0040CF18: lea eax, var_148
  loc_0040CF1E: push eax
  loc_0040CF1F: push 00000030h
  loc_0040CF21: lea ecx, var_138
  loc_0040CF27: push ecx
  loc_0040CF28: call [00401084h] ; rtcMsgBox
  loc_0040CF2E: lea edx, var_168
  loc_0040CF34: push edx
  loc_0040CF35: lea eax, var_158
  loc_0040CF3B: push eax
  loc_0040CF3C: lea ecx, var_148
  loc_0040CF42: push ecx
  loc_0040CF43: lea edx, var_138
  loc_0040CF49: push edx
  loc_0040CF4A: push 00000004h
  loc_0040CF4C: call [00401038h] ; __vbaFreeVarList
  loc_0040CF52: add esp, 00000014h
  loc_0040CF55: jmp 0041489Fh
  loc_0040CF5A: mov eax, Me
  loc_0040CF5D: mov ecx, [eax]
  loc_0040CF5F: mov edx, Me
  loc_0040CF62: push edx
  loc_0040CF63: call [ecx+000002FCh]
  loc_0040CF69: push eax
  loc_0040CF6A: lea eax, var_118
  loc_0040CF70: push eax
  loc_0040CF71: call [00401080h] ; __vbaObjSet
  loc_0040CF77: mov var_2C0, eax
  loc_0040CF7D: lea ecx, var_28C
  loc_0040CF83: push ecx
  loc_0040CF84: mov edx, var_2C0
  loc_0040CF8A: mov eax, [edx]
  loc_0040CF8C: mov ecx, var_2C0
  loc_0040CF92: push ecx
  loc_0040CF93: call [eax+000000E0h]
  loc_0040CF99: fnclex
  loc_0040CF9B: mov var_2C4, eax
  loc_0040CFA1: cmp var_2C4, 00000000h
  loc_0040CFA8: jge 0040CFD0h
  loc_0040CFAA: push 000000E0h
  loc_0040CFAF: push 00405354h
  loc_0040CFB4: mov edx, var_2C0
  loc_0040CFBA: push edx
  loc_0040CFBB: mov eax, var_2C4
  loc_0040CFC1: push eax
  loc_0040CFC2: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040CFC8: mov var_380, eax
  loc_0040CFCE: jmp 0040CFDAh
  loc_0040CFD0: mov var_380, 00000000h
  loc_0040CFDA: movsx ecx, var_28C
  loc_0040CFE1: sub ecx, 00000001h
  loc_0040CFE4: neg ecx
  loc_0040CFE6: sbb ecx, ecx
  loc_0040CFE8: inc ecx
  loc_0040CFE9: neg ecx
  loc_0040CFEB: mov var_2C8, cx
  loc_0040CFF2: lea ecx, var_118
  loc_0040CFF8: call [004011F0h] ; __vbaFreeObj
  loc_0040CFFE: movsx edx, var_2C8
  loc_0040D005: test edx, edx
  loc_0040D007: jz 0040D014h
  loc_0040D009: mov [0042303Eh], FFFFFFh
  loc_0040D012: jmp 0040D01Dh
  loc_0040D014: mov [0042303Eh], 0000h
  loc_0040D01D: mov eax, Me
  loc_0040D020: mov ecx, [eax]
  loc_0040D022: mov edx, Me
  loc_0040D025: push edx
  loc_0040D026: call [ecx+00000390h]
  loc_0040D02C: push eax
  loc_0040D02D: lea eax, var_118
  loc_0040D033: push eax
  loc_0040D034: call [00401080h] ; __vbaObjSet
  loc_0040D03A: mov var_2C0, eax
  loc_0040D040: push 00406244h ; "Cancel"
  loc_0040D045: mov ecx, var_2C0
  loc_0040D04B: mov edx, [ecx]
  loc_0040D04D: mov eax, var_2C0
  loc_0040D053: push eax
  loc_0040D054: call [edx+00000054h]
  loc_0040D057: fnclex
  loc_0040D059: mov var_2C4, eax
  loc_0040D05F: cmp var_2C4, 00000000h
  loc_0040D066: jge 0040D08Bh
  loc_0040D068: push 00000054h
  loc_0040D06A: push 00406128h
  loc_0040D06F: mov ecx, var_2C0
  loc_0040D075: push ecx
  loc_0040D076: mov edx, var_2C4
  loc_0040D07C: push edx
  loc_0040D07D: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040D083: mov var_384, eax
  loc_0040D089: jmp 0040D095h
  loc_0040D08B: mov var_384, 00000000h
  loc_0040D095: lea ecx, var_118
  loc_0040D09B: call [004011F0h] ; __vbaFreeObj
  loc_0040D0A1: call [004010A0h] ; rtcDoEvents
  loc_0040D0A7: mov eax, Me
  loc_0040D0AA: mov [eax+0000005Eh], 0000h
  loc_0040D0B0: movsx ecx, [00423032h]
  loc_0040D0B7: test ecx, ecx
  loc_0040D0B9: jz 0040DB5Dh
  loc_0040D0BF: mov edx, Me
  loc_0040D0C2: mov eax, [edx]
  loc_0040D0C4: mov ecx, Me
  loc_0040D0C7: push ecx
  loc_0040D0C8: call [eax+0000039Ch]
  loc_0040D0CE: push eax
  loc_0040D0CF: lea edx, var_118
  loc_0040D0D5: push edx
  loc_0040D0D6: call [00401080h] ; __vbaObjSet
  loc_0040D0DC: mov var_2C0, eax
  loc_0040D0E2: push 00406258h ; "Waiting for OK on align site"
  loc_0040D0E7: mov eax, var_2C0
  loc_0040D0ED: mov ecx, [eax]
  loc_0040D0EF: mov edx, var_2C0
  loc_0040D0F5: push edx
  loc_0040D0F6: call [ecx+00000054h]
  loc_0040D0F9: fnclex
  loc_0040D0FB: mov var_2C4, eax
  loc_0040D101: cmp var_2C4, 00000000h
  loc_0040D108: jge 0040D12Dh
  loc_0040D10A: push 00000054h
  loc_0040D10C: push 0040575Ch
  loc_0040D111: mov eax, var_2C0
  loc_0040D117: push eax
  loc_0040D118: mov ecx, var_2C4
  loc_0040D11E: push ecx
  loc_0040D11F: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040D125: mov var_388, eax
  loc_0040D12B: jmp 0040D137h
  loc_0040D12D: mov var_388, 00000000h
  loc_0040D137: lea ecx, var_118
  loc_0040D13D: call [004011F0h] ; __vbaFreeObj
  loc_0040D143: call [004010A0h] ; rtcDoEvents
  loc_0040D149: mov edx, 00406298h ; "Please align to the align site."
  loc_0040D14E: lea ecx, var_58
  loc_0040D151: call [00401178h] ; __vbaStrCopy
  loc_0040D157: mov edx, 004062DCh ; "PreAlignMessage"
  loc_0040D15C: lea ecx, var_C8
  loc_0040D162: call [00401178h] ; __vbaStrCopy
  loc_0040D168: lea edx, var_CC
  loc_0040D16E: push edx
  loc_0040D16F: lea eax, var_C8
  loc_0040D175: push eax
  loc_0040D176: mov ecx, var_C0
  loc_0040D17C: mov edx, [ecx]
  loc_0040D17E: mov eax, var_C0
  loc_0040D184: push eax
  loc_0040D185: call [edx+0000002Ch]
  loc_0040D188: fnclex
  loc_0040D18A: mov var_2C0, eax
  loc_0040D190: cmp var_2C0, 00000000h
  loc_0040D197: jge 0040D1BCh
  loc_0040D199: push 0000002Ch
  loc_0040D19B: push 00405B8Ch
  loc_0040D1A0: mov ecx, var_C0
  loc_0040D1A6: push ecx
  loc_0040D1A7: mov edx, var_2C0
  loc_0040D1AD: push edx
  loc_0040D1AE: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040D1B4: mov var_38C, eax
  loc_0040D1BA: jmp 0040D1C6h
  loc_0040D1BC: mov var_38C, 00000000h
  loc_0040D1C6: mov eax, var_CC
  loc_0040D1CC: push eax
  loc_0040D1CD: push 00000000h
  loc_0040D1CF: call [004010DCh] ; __vbaStrCmp
  loc_0040D1D5: neg eax
  loc_0040D1D7: sbb eax, eax
  loc_0040D1D9: neg eax
  loc_0040D1DB: neg eax
  loc_0040D1DD: mov var_2C4, ax
  loc_0040D1E4: lea ecx, var_CC
  loc_0040D1EA: push ecx
  loc_0040D1EB: lea edx, var_C8
  loc_0040D1F1: push edx
  loc_0040D1F2: push 00000002h
  loc_0040D1F4: call [00401180h] ; __vbaFreeStrList
  loc_0040D1FA: add esp, 0000000Ch
  loc_0040D1FD: movsx eax, var_2C4
  loc_0040D204: test eax, eax
  loc_0040D206: jz 0040D2D1h
  loc_0040D20C: mov edx, 004062DCh ; "PreAlignMessage"
  loc_0040D211: lea ecx, var_C8
  loc_0040D217: call [00401178h] ; __vbaStrCopy
  loc_0040D21D: lea ecx, var_CC
  loc_0040D223: push ecx
  loc_0040D224: lea edx, var_C8
  loc_0040D22A: push edx
  loc_0040D22B: mov eax, var_C0
  loc_0040D231: mov ecx, [eax]
  loc_0040D233: mov edx, var_C0
  loc_0040D239: push edx
  loc_0040D23A: call [ecx+0000002Ch]
  loc_0040D23D: fnclex
  loc_0040D23F: mov var_2C0, eax
  loc_0040D245: cmp var_2C0, 00000000h
  loc_0040D24C: jge 0040D271h
  loc_0040D24E: push 0000002Ch
  loc_0040D250: push 00405B8Ch
  loc_0040D255: mov eax, var_C0
  loc_0040D25B: push eax
  loc_0040D25C: mov ecx, var_2C0
  loc_0040D262: push ecx
  loc_0040D263: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040D269: mov var_390, eax
  loc_0040D26F: jmp 0040D27Bh
  loc_0040D271: mov var_390, 00000000h
  loc_0040D27B: mov edx, var_58
  loc_0040D27E: push edx
  loc_0040D27F: push 004054D8h ; vbCrLf
  loc_0040D284: call [00401050h] ; __vbaStrCat
  loc_0040D28A: mov edx, eax
  loc_0040D28C: lea ecx, var_D0
  loc_0040D292: call [004011D0h] ; __vbaStrMove
  loc_0040D298: push eax
  loc_0040D299: mov eax, var_CC
  loc_0040D29F: push eax
  loc_0040D2A0: call [00401050h] ; __vbaStrCat
  loc_0040D2A6: mov edx, eax
  loc_0040D2A8: lea ecx, var_58
  loc_0040D2AB: call [004011D0h] ; __vbaStrMove
  loc_0040D2B1: lea ecx, var_CC
  loc_0040D2B7: push ecx
  loc_0040D2B8: lea edx, var_D0
  loc_0040D2BE: push edx
  loc_0040D2BF: lea eax, var_C8
  loc_0040D2C5: push eax
  loc_0040D2C6: push 00000003h
  loc_0040D2C8: call [00401180h] ; __vbaFreeStrList
  loc_0040D2CE: add esp, 00000010h
  loc_0040D2D1: mov ecx, var_58
  loc_0040D2D4: push ecx
  loc_0040D2D5: push 004054D8h ; vbCrLf
  loc_0040D2DA: call [00401050h] ; __vbaStrCat
  loc_0040D2E0: mov edx, eax
  loc_0040D2E2: lea ecx, var_C8
  loc_0040D2E8: call [004011D0h] ; __vbaStrMove
  loc_0040D2EE: push eax
  loc_0040D2EF: push 00406300h ; "When complete, Click 'OK' to continue, or 'Cancel' to cancel."
  loc_0040D2F4: call [00401050h] ; __vbaStrCat
  loc_0040D2FA: mov edx, eax
  loc_0040D2FC: lea ecx, var_58
  loc_0040D2FF: call [004011D0h] ; __vbaStrMove
  loc_0040D305: lea ecx, var_C8
  loc_0040D30B: call [004011F4h] ; __vbaFreeStr
  loc_0040D311: mov var_150, 80020004h
  loc_0040D31B: mov var_158, 0000000Ah
  loc_0040D325: mov var_140, 80020004h
  loc_0040D32F: mov var_148, 0000000Ah
  loc_0040D339: mov var_260, 004050E8h ; "IMT LampElectrical Probing"
  loc_0040D343: mov var_268, 00000008h
  loc_0040D34D: lea edx, var_268
  loc_0040D353: lea ecx, var_138
  loc_0040D359: call [004011B4h] ; __vbaVarDup
  loc_0040D35F: lea edx, var_58
  loc_0040D362: mov var_250, edx
  loc_0040D368: mov var_258, 00004008h
  loc_0040D372: lea eax, var_158
  loc_0040D378: push eax
  loc_0040D379: lea ecx, var_148
  loc_0040D37F: push ecx
  loc_0040D380: lea edx, var_138
  loc_0040D386: push edx
  loc_0040D387: push 00000001h
  loc_0040D389: lea eax, var_258
  loc_0040D38F: push eax
  loc_0040D390: call [00401084h] ; rtcMsgBox
  loc_0040D396: mov ecx, eax
  loc_0040D398: call [004010ECh] ; __vbaI2I4
  loc_0040D39E: mov var_18, ax
  loc_0040D3A2: lea ecx, var_158
  loc_0040D3A8: push ecx
  loc_0040D3A9: lea edx, var_148
  loc_0040D3AF: push edx
  loc_0040D3B0: lea eax, var_138
  loc_0040D3B6: push eax
  loc_0040D3B7: push 00000003h
  loc_0040D3B9: call [00401038h] ; __vbaFreeVarList
  loc_0040D3BF: add esp, 00000010h
  loc_0040D3C2: movsx ecx, var_18
  loc_0040D3C6: cmp ecx, 00000002h
  loc_0040D3C9: jz 0040D3DAh
  loc_0040D3CB: mov edx, Me
  loc_0040D3CE: movsx eax, [edx+0000005Eh]
  loc_0040D3D2: test eax, eax
  loc_0040D3D4: jz 0040D508h
  loc_0040D3DA: push 00405B8Ch
  loc_0040D3DF: push 00000000h
  loc_0040D3E1: call [004011D4h] ; __vbaCastObj
  loc_0040D3E7: push eax
  loc_0040D3E8: lea ecx, var_C0
  loc_0040D3EE: push ecx
  loc_0040D3EF: call [00401080h] ; __vbaObjSet
  loc_0040D3F5: mov edx, Me
  loc_0040D3F8: mov eax, [edx]
  loc_0040D3FA: mov ecx, Me
  loc_0040D3FD: push ecx
  loc_0040D3FE: call [eax+0000039Ch]
  loc_0040D404: push eax
  loc_0040D405: lea edx, var_118
  loc_0040D40B: push edx
  loc_0040D40C: call [00401080h] ; __vbaObjSet
  loc_0040D412: mov var_2C0, eax
  loc_0040D418: push 00406380h ; "Ready"
  loc_0040D41D: mov eax, var_2C0
  loc_0040D423: mov ecx, [eax]
  loc_0040D425: mov edx, var_2C0
  loc_0040D42B: push edx
  loc_0040D42C: call [ecx+00000054h]
  loc_0040D42F: fnclex
  loc_0040D431: mov var_2C4, eax
  loc_0040D437: cmp var_2C4, 00000000h
  loc_0040D43E: jge 0040D463h
  loc_0040D440: push 00000054h
  loc_0040D442: push 0040575Ch
  loc_0040D447: mov eax, var_2C0
  loc_0040D44D: push eax
  loc_0040D44E: mov ecx, var_2C4
  loc_0040D454: push ecx
  loc_0040D455: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040D45B: mov var_394, eax
  loc_0040D461: jmp 0040D46Dh
  loc_0040D463: mov var_394, 00000000h
  loc_0040D46D: lea ecx, var_118
  loc_0040D473: call [004011F0h] ; __vbaFreeObj
  loc_0040D479: mov edx, Me
  loc_0040D47C: mov eax, [edx]
  loc_0040D47E: mov ecx, Me
  loc_0040D481: push ecx
  loc_0040D482: call [eax+00000390h]
  loc_0040D488: push eax
  loc_0040D489: lea edx, var_118
  loc_0040D48F: push edx
  loc_0040D490: call [00401080h] ; __vbaObjSet
  loc_0040D496: mov var_2C0, eax
  loc_0040D49C: push 00406390h ; "Go"
  loc_0040D4A1: mov eax, var_2C0
  loc_0040D4A7: mov ecx, [eax]
  loc_0040D4A9: mov edx, var_2C0
  loc_0040D4AF: push edx
  loc_0040D4B0: call [ecx+00000054h]
  loc_0040D4B3: fnclex
  loc_0040D4B5: mov var_2C4, eax
  loc_0040D4BB: cmp var_2C4, 00000000h
  loc_0040D4C2: jge 0040D4E7h
  loc_0040D4C4: push 00000054h
  loc_0040D4C6: push 00406128h
  loc_0040D4CB: mov eax, var_2C0
  loc_0040D4D1: push eax
  loc_0040D4D2: mov ecx, var_2C4
  loc_0040D4D8: push ecx
  loc_0040D4D9: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040D4DF: mov var_398, eax
  loc_0040D4E5: jmp 0040D4F1h
  loc_0040D4E7: mov var_398, 00000000h
  loc_0040D4F1: lea ecx, var_118
  loc_0040D4F7: call [004011F0h] ; __vbaFreeObj
  loc_0040D4FD: call [004010A0h] ; rtcDoEvents
  loc_0040D503: jmp 0041489Fh
  loc_0040D508: mov edx, 0040639Ch ; "XMoveFirstFromAlignSite"
  loc_0040D50D: lea ecx, var_C8
  loc_0040D513: call [00401178h] ; __vbaStrCopy
  loc_0040D519: lea edx, var_CC
  loc_0040D51F: push edx
  loc_0040D520: lea eax, var_C8
  loc_0040D526: push eax
  loc_0040D527: mov ecx, var_C0
  loc_0040D52D: mov edx, [ecx]
  loc_0040D52F: mov eax, var_C0
  loc_0040D535: push eax
  loc_0040D536: call [edx+0000002Ch]
  loc_0040D539: fnclex
  loc_0040D53B: mov var_2C0, eax
  loc_0040D541: cmp var_2C0, 00000000h
  loc_0040D548: jge 0040D56Dh
  loc_0040D54A: push 0000002Ch
  loc_0040D54C: push 00405B8Ch
  loc_0040D551: mov ecx, var_C0
  loc_0040D557: push ecx
  loc_0040D558: mov edx, var_2C0
  loc_0040D55E: push edx
  loc_0040D55F: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040D565: mov var_39C, eax
  loc_0040D56B: jmp 0040D577h
  loc_0040D56D: mov var_39C, 00000000h
  loc_0040D577: mov eax, var_CC
  loc_0040D57D: mov var_334, eax
  loc_0040D583: mov var_CC, 00000000h
  loc_0040D58D: mov ecx, var_334
  loc_0040D593: mov var_130, ecx
  loc_0040D599: mov var_138, 00000008h
  loc_0040D5A3: lea edx, var_138
  loc_0040D5A9: push edx
  loc_0040D5AA: call 0041DBB0h
  loc_0040D5AF: fstp real8 ptr var_54
  loc_0040D5B2: lea ecx, var_C8
  loc_0040D5B8: call [004011F4h] ; __vbaFreeStr
  loc_0040D5BE: lea ecx, var_138
  loc_0040D5C4: call [00401020h] ; __vbaFreeVar
  loc_0040D5CA: mov edx, 004063DCh ; "YMoveFirstFromAlignSite"
  loc_0040D5CF: lea ecx, var_C8
  loc_0040D5D5: call [00401178h] ; __vbaStrCopy
  loc_0040D5DB: lea eax, var_CC
  loc_0040D5E1: push eax
  loc_0040D5E2: lea ecx, var_C8
  loc_0040D5E8: push ecx
  loc_0040D5E9: mov edx, var_C0
  loc_0040D5EF: mov eax, [edx]
  loc_0040D5F1: mov ecx, var_C0
  loc_0040D5F7: push ecx
  loc_0040D5F8: call [eax+0000002Ch]
  loc_0040D5FB: fnclex
  loc_0040D5FD: mov var_2C0, eax
  loc_0040D603: cmp var_2C0, 00000000h
  loc_0040D60A: jge 0040D62Fh
  loc_0040D60C: push 0000002Ch
  loc_0040D60E: push 00405B8Ch
  loc_0040D613: mov edx, var_C0
  loc_0040D619: push edx
  loc_0040D61A: mov eax, var_2C0
  loc_0040D620: push eax
  loc_0040D621: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040D627: mov var_3A0, eax
  loc_0040D62D: jmp 0040D639h
  loc_0040D62F: mov var_3A0, 00000000h
  loc_0040D639: mov ecx, var_CC
  loc_0040D63F: mov var_338, ecx
  loc_0040D645: mov var_CC, 00000000h
  loc_0040D64F: mov edx, var_338
  loc_0040D655: mov var_130, edx
  loc_0040D65B: mov var_138, 00000008h
  loc_0040D665: lea eax, var_138
  loc_0040D66B: push eax
  loc_0040D66C: call 0041DBB0h
  loc_0040D671: fstp real8 ptr var_90
  loc_0040D677: lea ecx, var_C8
  loc_0040D67D: call [004011F4h] ; __vbaFreeStr
  loc_0040D683: lea ecx, var_138
  loc_0040D689: call [00401020h] ; __vbaFreeVar
  loc_0040D68F: fld real8 ptr var_54
  loc_0040D692: fcomp real8 ptr [00401288h]
  loc_0040D698: fnstsw ax
  loc_0040D69A: test ah, 40h
  loc_0040D69D: jz 0040D6ABh
  loc_0040D69F: mov var_3A4, 00000001h
  loc_0040D6A9: jmp 0040D6B5h
  loc_0040D6AB: mov var_3A4, 00000000h
  loc_0040D6B5: fld real8 ptr var_90
  loc_0040D6BB: fcomp real8 ptr [00401288h]
  loc_0040D6C1: fnstsw ax
  loc_0040D6C3: test ah, 40h
  loc_0040D6C6: jz 0040D6D4h
  loc_0040D6C8: mov var_3A8, 00000001h
  loc_0040D6D2: jmp 0040D6DEh
  loc_0040D6D4: mov var_3A8, 00000000h
  loc_0040D6DE: mov ecx, var_3A4
  loc_0040D6E4: and ecx, var_3A8
  loc_0040D6EA: test ecx, ecx
  loc_0040D6EC: jnz 0040DB5Dh
  loc_0040D6F2: mov edx, Me
  loc_0040D6F5: mov eax, [edx]
  loc_0040D6F7: mov ecx, Me
  loc_0040D6FA: push ecx
  loc_0040D6FB: call [eax+0000039Ch]
  loc_0040D701: push eax
  loc_0040D702: lea edx, var_118
  loc_0040D708: push edx
  loc_0040D709: call [00401080h] ; __vbaObjSet
  loc_0040D70F: mov var_2C0, eax
  loc_0040D715: push 00406410h ; "Moving to first site"
  loc_0040D71A: mov eax, var_2C0
  loc_0040D720: mov ecx, [eax]
  loc_0040D722: mov edx, var_2C0
  loc_0040D728: push edx
  loc_0040D729: call [ecx+00000054h]
  loc_0040D72C: fnclex
  loc_0040D72E: mov var_2C4, eax
  loc_0040D734: cmp var_2C4, 00000000h
  loc_0040D73B: jge 0040D760h
  loc_0040D73D: push 00000054h
  loc_0040D73F: push 0040575Ch
  loc_0040D744: mov eax, var_2C0
  loc_0040D74A: push eax
  loc_0040D74B: mov ecx, var_2C4
  loc_0040D751: push ecx
  loc_0040D752: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040D758: mov var_3AC, eax
  loc_0040D75E: jmp 0040D76Ah
  loc_0040D760: mov var_3AC, 00000000h
  loc_0040D76A: lea ecx, var_118
  loc_0040D770: call [004011F0h] ; __vbaFreeObj
  loc_0040D776: call [004010A0h] ; rtcDoEvents
  loc_0040D77C: mov var_250, 00406440h ; "MMX"
  loc_0040D786: mov var_258, 00000008h
  loc_0040D790: mov edx, var_50
  loc_0040D793: push edx
  loc_0040D794: mov eax, var_54
  loc_0040D797: push eax
  loc_0040D798: call [00401104h] ; __vbaStrR8
  loc_0040D79E: mov var_130, eax
  loc_0040D7A4: mov var_138, 00000008h
  loc_0040D7AE: lea ecx, var_138
  loc_0040D7B4: push ecx
  loc_0040D7B5: lea edx, var_148
  loc_0040D7BB: push edx
  loc_0040D7BC: call [004010A4h] ; rtcTrimVar
  loc_0040D7C2: mov var_260, 0040644Ch ; "Y"
  loc_0040D7CC: mov var_268, 00000008h
  loc_0040D7D6: mov eax, var_8C
  loc_0040D7DC: push eax
  loc_0040D7DD: mov ecx, var_90
  loc_0040D7E3: push ecx
  loc_0040D7E4: call [00401104h] ; __vbaStrR8
  loc_0040D7EA: mov var_170, eax
  loc_0040D7F0: mov var_178, 00000008h
  loc_0040D7FA: lea edx, var_178
  loc_0040D800: push edx
  loc_0040D801: lea eax, var_188
  loc_0040D807: push eax
  loc_0040D808: call [004010A4h] ; rtcTrimVar
  loc_0040D80E: lea ecx, var_258
  loc_0040D814: push ecx
  loc_0040D815: lea edx, var_148
  loc_0040D81B: push edx
  loc_0040D81C: lea eax, var_158
  loc_0040D822: push eax
  loc_0040D823: call [004011ACh] ; __vbaVarAdd
  loc_0040D829: push eax
  loc_0040D82A: lea ecx, var_268
  loc_0040D830: push ecx
  loc_0040D831: lea edx, var_168
  loc_0040D837: push edx
  loc_0040D838: call [004011ACh] ; __vbaVarAdd
  loc_0040D83E: push eax
  loc_0040D83F: lea eax, var_188
  loc_0040D845: push eax
  loc_0040D846: lea ecx, var_198
  loc_0040D84C: push ecx
  loc_0040D84D: call [004011ACh] ; __vbaVarAdd
  loc_0040D853: push eax
  loc_0040D854: call [00401030h] ; __vbaStrVarMove
  loc_0040D85A: mov edx, eax
  loc_0040D85C: lea ecx, var_58
  loc_0040D85F: call [004011D0h] ; __vbaStrMove
  loc_0040D865: lea edx, var_198
  loc_0040D86B: push edx
  loc_0040D86C: lea eax, var_188
  loc_0040D872: push eax
  loc_0040D873: lea ecx, var_168
  loc_0040D879: push ecx
  loc_0040D87A: lea edx, var_178
  loc_0040D880: push edx
  loc_0040D881: lea eax, var_158
  loc_0040D887: push eax
  loc_0040D888: lea ecx, var_148
  loc_0040D88E: push ecx
  loc_0040D88F: lea edx, var_138
  loc_0040D895: push edx
  loc_0040D896: push 00000007h
  loc_0040D898: call [00401038h] ; __vbaFreeVarList
  loc_0040D89E: add esp, 00000020h
  loc_0040D8A1: mov var_130, FFFFFFFFh
  loc_0040D8AB: mov var_138, 0000000Bh
  loc_0040D8B5: mov edx, 00406454h ; "2001X"
  loc_0040D8BA: lea ecx, var_C8
  loc_0040D8C0: call [00401178h] ; __vbaStrCopy
  loc_0040D8C6: lea eax, var_138
  loc_0040D8CC: push eax
  loc_0040D8CD: lea ecx, var_58
  loc_0040D8D0: push ecx
  loc_0040D8D1: lea edx, var_C8
  loc_0040D8D7: push edx
  loc_0040D8D8: lea eax, var_148
  loc_0040D8DE: push eax
  loc_0040D8DF: call 0041CA40h
  loc_0040D8E4: lea edx, var_148
  loc_0040D8EA: lea ecx, var_84
  loc_0040D8F0: call [00401014h] ; __vbaVarMove
  loc_0040D8F6: lea ecx, var_C8
  loc_0040D8FC: call [004011F4h] ; __vbaFreeStr
  loc_0040D902: lea ecx, var_138
  loc_0040D908: call [00401020h] ; __vbaFreeVar
  loc_0040D90E: lea ecx, var_84
  loc_0040D914: push ecx
  loc_0040D915: call [00401044h] ; __vbaStrErrVarCopy
  loc_0040D91B: mov edx, eax
  loc_0040D91D: lea ecx, var_C8
  loc_0040D923: call [004011D0h] ; __vbaStrMove
  loc_0040D929: push eax
  loc_0040D92A: push 00406464h ; "MC"
  loc_0040D92F: call [004010DCh] ; __vbaStrCmp
  loc_0040D935: neg eax
  loc_0040D937: sbb eax, eax
  loc_0040D939: neg eax
  loc_0040D93B: neg eax
  loc_0040D93D: mov var_2C0, ax
  loc_0040D944: lea ecx, var_C8
  loc_0040D94A: call [004011F4h] ; __vbaFreeStr
  loc_0040D950: movsx edx, var_2C0
  loc_0040D957: test edx, edx
  loc_0040D959: jz 0040DB5Dh
  loc_0040D95F: mov var_160, 80020004h
  loc_0040D969: mov var_168, 0000000Ah
  loc_0040D973: mov var_150, 80020004h
  loc_0040D97D: mov var_158, 0000000Ah
  loc_0040D987: mov var_250, 004050E8h ; "IMT LampElectrical Probing"
  loc_0040D991: mov var_258, 00000008h
  loc_0040D99B: lea edx, var_258
  loc_0040D9A1: lea ecx, var_148
  loc_0040D9A7: call [004011B4h] ; __vbaVarDup
  loc_0040D9AD: push 00406470h ; "Prober command '"
  loc_0040D9B2: mov eax, var_58
  loc_0040D9B5: push eax
  loc_0040D9B6: call [00401050h] ; __vbaStrCat
  loc_0040D9BC: mov edx, eax
  loc_0040D9BE: lea ecx, var_C8
  loc_0040D9C4: call [004011D0h] ; __vbaStrMove
  loc_0040D9CA: push eax
  loc_0040D9CB: push 00406498h ; "' failed to return 'MC', instead said:"
  loc_0040D9D0: call [00401050h] ; __vbaStrCat
  loc_0040D9D6: mov edx, eax
  loc_0040D9D8: lea ecx, var_CC
  loc_0040D9DE: call [004011D0h] ; __vbaStrMove
  loc_0040D9E4: push eax
  loc_0040D9E5: push 004054D8h ; vbCrLf
  loc_0040D9EA: call [00401050h] ; __vbaStrCat
  loc_0040D9F0: mov edx, eax
  loc_0040D9F2: lea ecx, var_D0
  loc_0040D9F8: call [004011D0h] ; __vbaStrMove
  loc_0040D9FE: push eax
  loc_0040D9FF: lea ecx, var_84
  loc_0040DA05: push ecx
  loc_0040DA06: call [00401044h] ; __vbaStrErrVarCopy
  loc_0040DA0C: mov edx, eax
  loc_0040DA0E: lea ecx, var_D4
  loc_0040DA14: call [004011D0h] ; __vbaStrMove
  loc_0040DA1A: push eax
  loc_0040DA1B: call [00401050h] ; __vbaStrCat
  loc_0040DA21: mov edx, eax
  loc_0040DA23: lea ecx, var_D8
  loc_0040DA29: call [004011D0h] ; __vbaStrMove
  loc_0040DA2F: push eax
  loc_0040DA30: push 004054D8h ; vbCrLf
  loc_0040DA35: call [00401050h] ; __vbaStrCat
  loc_0040DA3B: mov edx, eax
  loc_0040DA3D: lea ecx, var_DC
  loc_0040DA43: call [004011D0h] ; __vbaStrMove
  loc_0040DA49: push eax
  loc_0040DA4A: push 004064ECh ; "Continue anyway?"
  loc_0040DA4F: call [00401050h] ; __vbaStrCat
  loc_0040DA55: mov var_130, eax
  loc_0040DA5B: mov var_138, 00000008h
  loc_0040DA65: lea edx, var_168
  loc_0040DA6B: push edx
  loc_0040DA6C: lea eax, var_158
  loc_0040DA72: push eax
  loc_0040DA73: lea ecx, var_148
  loc_0040DA79: push ecx
  loc_0040DA7A: push 00000004h
  loc_0040DA7C: lea edx, var_138
  loc_0040DA82: push edx
  loc_0040DA83: call [00401084h] ; rtcMsgBox
  loc_0040DA89: mov ecx, eax
  loc_0040DA8B: call [004010ECh] ; __vbaI2I4
  loc_0040DA91: mov var_18, ax
  loc_0040DA95: lea eax, var_DC
  loc_0040DA9B: push eax
  loc_0040DA9C: lea ecx, var_D8
  loc_0040DAA2: push ecx
  loc_0040DAA3: lea edx, var_D4
  loc_0040DAA9: push edx
  loc_0040DAAA: lea eax, var_D0
  loc_0040DAB0: push eax
  loc_0040DAB1: lea ecx, var_CC
  loc_0040DAB7: push ecx
  loc_0040DAB8: lea edx, var_C8
  loc_0040DABE: push edx
  loc_0040DABF: push 00000006h
  loc_0040DAC1: call [00401180h] ; __vbaFreeStrList
  loc_0040DAC7: add esp, 0000001Ch
  loc_0040DACA: lea eax, var_168
  loc_0040DAD0: push eax
  loc_0040DAD1: lea ecx, var_158
  loc_0040DAD7: push ecx
  loc_0040DAD8: lea edx, var_148
  loc_0040DADE: push edx
  loc_0040DADF: lea eax, var_138
  loc_0040DAE5: push eax
  loc_0040DAE6: push 00000004h
  loc_0040DAE8: call [00401038h] ; __vbaFreeVarList
  loc_0040DAEE: add esp, 00000014h
  loc_0040DAF1: movsx ecx, var_18
  loc_0040DAF5: cmp ecx, 00000007h
  loc_0040DAF8: jnz 0040DB5Dh
  loc_0040DAFA: lea edx, var_138
  loc_0040DB00: push edx
  loc_0040DB01: mov eax, Me
  loc_0040DB04: mov ecx, [eax]
  loc_0040DB06: mov edx, Me
  loc_0040DB09: push edx
  loc_0040DB0A: call [ecx+00000704h]
  loc_0040DB10: mov var_2C0, eax
  loc_0040DB16: cmp var_2C0, 00000000h
  loc_0040DB1D: jge 0040DB42h
  loc_0040DB1F: push 00000704h
  loc_0040DB24: push 0040579Ch ; "#]=VｫoyAｷ ;ﾑs：ﾚLabel12"
  loc_0040DB29: mov eax, Me
  loc_0040DB2C: push eax
  loc_0040DB2D: mov ecx, var_2C0
  loc_0040DB33: push ecx
  loc_0040DB34: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040DB3A: mov var_3B0, eax
  loc_0040DB40: jmp 0040DB4Ch
  loc_0040DB42: mov var_3B0, 00000000h
  loc_0040DB4C: lea ecx, var_138
  loc_0040DB52: call [00401020h] ; __vbaFreeVar
  loc_0040DB58: jmp 0041489Fh
  loc_0040DB5D: movsx edx, [00423032h]
  loc_0040DB64: test edx, edx
  loc_0040DB66: jz 004109A9h
  loc_0040DB6C: mov eax, Me
  loc_0040DB6F: mov ecx, [eax]
  loc_0040DB71: mov edx, Me
  loc_0040DB74: push edx
  loc_0040DB75: call [ecx+0000039Ch]
  loc_0040DB7B: push eax
  loc_0040DB7C: lea eax, var_118
  loc_0040DB82: push eax
  loc_0040DB83: call [00401080h] ; __vbaObjSet
  loc_0040DB89: mov var_2C0, eax
  loc_0040DB8F: push 00406514h ; "Waiting final OK to begin probing"
  loc_0040DB94: mov ecx, var_2C0
  loc_0040DB9A: mov edx, [ecx]
  loc_0040DB9C: mov eax, var_2C0
  loc_0040DBA2: push eax
  loc_0040DBA3: call [edx+00000054h]
  loc_0040DBA6: fnclex
  loc_0040DBA8: mov var_2C4, eax
  loc_0040DBAE: cmp var_2C4, 00000000h
  loc_0040DBB5: jge 0040DBDAh
  loc_0040DBB7: push 00000054h
  loc_0040DBB9: push 0040575Ch
  loc_0040DBBE: mov ecx, var_2C0
  loc_0040DBC4: push ecx
  loc_0040DBC5: mov edx, var_2C4
  loc_0040DBCB: push edx
  loc_0040DBCC: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040DBD2: mov var_3B4, eax
  loc_0040DBD8: jmp 0040DBE4h
  loc_0040DBDA: mov var_3B4, 00000000h
  loc_0040DBE4: lea ecx, var_118
  loc_0040DBEA: call [004011F0h] ; __vbaFreeObj
  loc_0040DBF0: call [004010A0h] ; rtcDoEvents
  loc_0040DBF6: push 0040655Ch ; "Align of wafer complete. "
  loc_0040DBFB: push 004054D8h ; vbCrLf
  loc_0040DC00: call [00401050h] ; __vbaStrCat
  loc_0040DC06: mov edx, eax
  loc_0040DC08: lea ecx, var_C8
  loc_0040DC0E: call [004011D0h] ; __vbaStrMove
  loc_0040DC14: push eax
  loc_0040DC15: push 004065ACh ; "Click 'OK' to commence probing, or 'Cancel' as the last chance to abort."
  loc_0040DC1A: call [00401050h] ; __vbaStrCat
  loc_0040DC20: mov edx, eax
  loc_0040DC22: lea ecx, var_CC
  loc_0040DC28: call [004011D0h] ; __vbaStrMove
  loc_0040DC2E: push eax
  loc_0040DC2F: push 004054D8h ; vbCrLf
  loc_0040DC34: call [00401050h] ; __vbaStrCat
  loc_0040DC3A: mov edx, eax
  loc_0040DC3C: lea ecx, var_D0
  loc_0040DC42: call [004011D0h] ; __vbaStrMove
  loc_0040DC48: push eax
  loc_0040DC49: push 00406644h ; "You MUST now check the 'Z' height on the prober lower key pad "
  loc_0040DC4E: call [00401050h] ; __vbaStrCat
  loc_0040DC54: mov edx, eax
  loc_0040DC56: lea ecx, var_D4
  loc_0040DC5C: call [004011D0h] ; __vbaStrMove
  loc_0040DC62: push eax
  loc_0040DC63: push 004066C8h ; "and be sure the stage is raised so that the probe tips contact the wafer! "
  loc_0040DC68: call [00401050h] ; __vbaStrCat
  loc_0040DC6E: mov edx, eax
  loc_0040DC70: lea ecx, var_D8
  loc_0040DC76: call [004011D0h] ; __vbaStrMove
  loc_0040DC7C: push eax
  loc_0040DC7D: push 00406798h ; "The Green light on the edge sensor box should then be on."
  loc_0040DC82: call [00401050h] ; __vbaStrCat
  loc_0040DC88: mov edx, eax
  loc_0040DC8A: lea ecx, var_58
  loc_0040DC8D: call [004011D0h] ; __vbaStrMove
  loc_0040DC93: lea eax, var_D8
  loc_0040DC99: push eax
  loc_0040DC9A: lea ecx, var_D4
  loc_0040DCA0: push ecx
  loc_0040DCA1: lea edx, var_D0
  loc_0040DCA7: push edx
  loc_0040DCA8: lea eax, var_CC
  loc_0040DCAE: push eax
  loc_0040DCAF: lea ecx, var_C8
  loc_0040DCB5: push ecx
  loc_0040DCB6: push 00000005h
  loc_0040DCB8: call [00401180h] ; __vbaFreeStrList
  loc_0040DCBE: add esp, 00000018h
  loc_0040DCC1: mov var_150, 80020004h
  loc_0040DCCB: mov var_158, 0000000Ah
  loc_0040DCD5: mov var_140, 80020004h
  loc_0040DCDF: mov var_148, 0000000Ah
  loc_0040DCE9: push 004050E8h ; "IMT LampElectrical Probing"
  loc_0040DCEE: push 00406810h ; " Last chance to abort!"
  loc_0040DCF3: call [00401050h] ; __vbaStrCat
  loc_0040DCF9: mov var_130, eax
  loc_0040DCFF: mov var_138, 00000008h
  loc_0040DD09: lea edx, var_58
  loc_0040DD0C: mov var_250, edx
  loc_0040DD12: mov var_258, 00004008h
  loc_0040DD1C: lea eax, var_158
  loc_0040DD22: push eax
  loc_0040DD23: lea ecx, var_148
  loc_0040DD29: push ecx
  loc_0040DD2A: lea edx, var_138
  loc_0040DD30: push edx
  loc_0040DD31: push 00000001h
  loc_0040DD33: lea eax, var_258
  loc_0040DD39: push eax
  loc_0040DD3A: call [00401084h] ; rtcMsgBox
  loc_0040DD40: mov ecx, eax
  loc_0040DD42: call [004010ECh] ; __vbaI2I4
  loc_0040DD48: mov var_18, ax
  loc_0040DD4C: lea ecx, var_158
  loc_0040DD52: push ecx
  loc_0040DD53: lea edx, var_148
  loc_0040DD59: push edx
  loc_0040DD5A: lea eax, var_138
  loc_0040DD60: push eax
  loc_0040DD61: push 00000003h
  loc_0040DD63: call [00401038h] ; __vbaFreeVarList
  loc_0040DD69: add esp, 00000010h
  loc_0040DD6C: mov edx, 00406844h ; "Iterations"
  loc_0040DD71: lea ecx, var_C8
  loc_0040DD77: call [00401178h] ; __vbaStrCopy
  loc_0040DD7D: lea ecx, var_CC
  loc_0040DD83: push ecx
  loc_0040DD84: lea edx, var_C8
  loc_0040DD8A: push edx
  loc_0040DD8B: mov eax, var_C0
  loc_0040DD91: mov ecx, [eax]
  loc_0040DD93: mov edx, var_C0
  loc_0040DD99: push edx
  loc_0040DD9A: call [ecx+0000002Ch]
  loc_0040DD9D: fnclex
  loc_0040DD9F: mov var_2C0, eax
  loc_0040DDA5: cmp var_2C0, 00000000h
  loc_0040DDAC: jge 0040DDD1h
  loc_0040DDAE: push 0000002Ch
  loc_0040DDB0: push 00405B8Ch
  loc_0040DDB5: mov eax, var_C0
  loc_0040DDBB: push eax
  loc_0040DDBC: mov ecx, var_2C0
  loc_0040DDC2: push ecx
  loc_0040DDC3: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040DDC9: mov var_3B8, eax
  loc_0040DDCF: jmp 0040DDDBh
  loc_0040DDD1: mov var_3B8, 00000000h
  loc_0040DDDB: mov edx, var_CC
  loc_0040DDE1: push edx
  loc_0040DDE2: push 00000000h
  loc_0040DDE4: call [004010DCh] ; __vbaStrCmp
  loc_0040DDEA: neg eax
  loc_0040DDEC: sbb eax, eax
  loc_0040DDEE: inc eax
  loc_0040DDEF: neg eax
  loc_0040DDF1: mov var_2C4, ax
  loc_0040DDF8: lea eax, var_CC
  loc_0040DDFE: push eax
  loc_0040DDFF: lea ecx, var_C8
  loc_0040DE05: push ecx
  loc_0040DE06: push 00000002h
  loc_0040DE08: call [00401180h] ; __vbaFreeStrList
  loc_0040DE0E: add esp, 0000000Ch
  loc_0040DE11: movsx edx, var_2C4
  loc_0040DE18: test edx, edx
  loc_0040DE1A: jz 0040DEE8h
  loc_0040DE20: mov var_160, 80020004h
  loc_0040DE2A: mov var_168, 0000000Ah
  loc_0040DE34: mov var_150, 80020004h
  loc_0040DE3E: mov var_158, 0000000Ah
  loc_0040DE48: mov var_260, 004050E8h ; "IMT LampElectrical Probing"
  loc_0040DE52: mov var_268, 00000008h
  loc_0040DE5C: lea edx, var_268
  loc_0040DE62: lea ecx, var_148
  loc_0040DE68: call [004011B4h] ; __vbaVarDup
  loc_0040DE6E: mov var_250, 00406860h ; "No Iterations parameter in recipe"
  loc_0040DE78: mov var_258, 00000008h
  loc_0040DE82: lea edx, var_258
  loc_0040DE88: lea ecx, var_138
  loc_0040DE8E: call [004011B4h] ; __vbaVarDup
  loc_0040DE94: lea eax, var_168
  loc_0040DE9A: push eax
  loc_0040DE9B: lea ecx, var_158
  loc_0040DEA1: push ecx
  loc_0040DEA2: lea edx, var_148
  loc_0040DEA8: push edx
  loc_0040DEA9: push 00000010h
  loc_0040DEAB: lea eax, var_138
  loc_0040DEB1: push eax
  loc_0040DEB2: call [00401084h] ; rtcMsgBox
  loc_0040DEB8: lea ecx, var_168
  loc_0040DEBE: push ecx
  loc_0040DEBF: lea edx, var_158
  loc_0040DEC5: push edx
  loc_0040DEC6: lea eax, var_148
  loc_0040DECC: push eax
  loc_0040DECD: lea ecx, var_138
  loc_0040DED3: push ecx
  loc_0040DED4: push 00000004h
  loc_0040DED6: call [00401038h] ; __vbaFreeVarList
  loc_0040DEDC: add esp, 00000014h
  loc_0040DEDF: mov edx, Me
  loc_0040DEE2: mov [edx+0000005Eh], FFFFFFh
  loc_0040DEE8: mov edx, 004068A8h ; "MeterDelay"
  loc_0040DEED: lea ecx, var_C8
  loc_0040DEF3: call [00401178h] ; __vbaStrCopy
  loc_0040DEF9: lea eax, var_CC
  loc_0040DEFF: push eax
  loc_0040DF00: lea ecx, var_C8
  loc_0040DF06: push ecx
  loc_0040DF07: mov edx, var_C0
  loc_0040DF0D: mov eax, [edx]
  loc_0040DF0F: mov ecx, var_C0
  loc_0040DF15: push ecx
  loc_0040DF16: call [eax+0000002Ch]
  loc_0040DF19: fnclex
  loc_0040DF1B: mov var_2C0, eax
  loc_0040DF21: cmp var_2C0, 00000000h
  loc_0040DF28: jge 0040DF4Dh
  loc_0040DF2A: push 0000002Ch
  loc_0040DF2C: push 00405B8Ch
  loc_0040DF31: mov edx, var_C0
  loc_0040DF37: push edx
  loc_0040DF38: mov eax, var_2C0
  loc_0040DF3E: push eax
  loc_0040DF3F: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040DF45: mov var_3BC, eax
  loc_0040DF4B: jmp 0040DF57h
  loc_0040DF4D: mov var_3BC, 00000000h
  loc_0040DF57: mov ecx, var_CC
  loc_0040DF5D: push ecx
  loc_0040DF5E: push 00000000h
  loc_0040DF60: call [004010DCh] ; __vbaStrCmp
  loc_0040DF66: neg eax
  loc_0040DF68: sbb eax, eax
  loc_0040DF6A: inc eax
  loc_0040DF6B: neg eax
  loc_0040DF6D: mov var_2C4, ax
  loc_0040DF74: lea edx, var_CC
  loc_0040DF7A: push edx
  loc_0040DF7B: lea eax, var_C8
  loc_0040DF81: push eax
  loc_0040DF82: push 00000002h
  loc_0040DF84: call [00401180h] ; __vbaFreeStrList
  loc_0040DF8A: add esp, 0000000Ch
  loc_0040DF8D: movsx ecx, var_2C4
  loc_0040DF94: test ecx, ecx
  loc_0040DF96: jz 0040E064h
  loc_0040DF9C: mov var_160, 80020004h
  loc_0040DFA6: mov var_168, 0000000Ah
  loc_0040DFB0: mov var_150, 80020004h
  loc_0040DFBA: mov var_158, 0000000Ah
  loc_0040DFC4: mov var_260, 004050E8h ; "IMT LampElectrical Probing"
  loc_0040DFCE: mov var_268, 00000008h
  loc_0040DFD8: lea edx, var_268
  loc_0040DFDE: lea ecx, var_148
  loc_0040DFE4: call [004011B4h] ; __vbaVarDup
  loc_0040DFEA: mov var_250, 004068C4h ; "No MeterDelay parameter in recipe."
  loc_0040DFF4: mov var_258, 00000008h
  loc_0040DFFE: lea edx, var_258
  loc_0040E004: lea ecx, var_138
  loc_0040E00A: call [004011B4h] ; __vbaVarDup
  loc_0040E010: lea edx, var_168
  loc_0040E016: push edx
  loc_0040E017: lea eax, var_158
  loc_0040E01D: push eax
  loc_0040E01E: lea ecx, var_148
  loc_0040E024: push ecx
  loc_0040E025: push 00000010h
  loc_0040E027: lea edx, var_138
  loc_0040E02D: push edx
  loc_0040E02E: call [00401084h] ; rtcMsgBox
  loc_0040E034: lea eax, var_168
  loc_0040E03A: push eax
  loc_0040E03B: lea ecx, var_158
  loc_0040E041: push ecx
  loc_0040E042: lea edx, var_148
  loc_0040E048: push edx
  loc_0040E049: lea eax, var_138
  loc_0040E04F: push eax
  loc_0040E050: push 00000004h
  loc_0040E052: call [00401038h] ; __vbaFreeVarList
  loc_0040E058: add esp, 00000014h
  loc_0040E05B: mov ecx, Me
  loc_0040E05E: mov [ecx+0000005Eh], FFFFFFh
  loc_0040E064: mov edx, 00406910h ; "Averages"
  loc_0040E069: lea ecx, var_C8
  loc_0040E06F: call [00401178h] ; __vbaStrCopy
  loc_0040E075: lea edx, var_CC
  loc_0040E07B: push edx
  loc_0040E07C: lea eax, var_C8
  loc_0040E082: push eax
  loc_0040E083: mov ecx, var_C0
  loc_0040E089: mov edx, [ecx]
  loc_0040E08B: mov eax, var_C0
  loc_0040E091: push eax
  loc_0040E092: call [edx+0000002Ch]
  loc_0040E095: fnclex
  loc_0040E097: mov var_2C0, eax
  loc_0040E09D: cmp var_2C0, 00000000h
  loc_0040E0A4: jge 0040E0C9h
  loc_0040E0A6: push 0000002Ch
  loc_0040E0A8: push 00405B8Ch
  loc_0040E0AD: mov ecx, var_C0
  loc_0040E0B3: push ecx
  loc_0040E0B4: mov edx, var_2C0
  loc_0040E0BA: push edx
  loc_0040E0BB: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040E0C1: mov var_3C0, eax
  loc_0040E0C7: jmp 0040E0D3h
  loc_0040E0C9: mov var_3C0, 00000000h
  loc_0040E0D3: mov eax, var_CC
  loc_0040E0D9: push eax
  loc_0040E0DA: push 00000000h
  loc_0040E0DC: call [004010DCh] ; __vbaStrCmp
  loc_0040E0E2: neg eax
  loc_0040E0E4: sbb eax, eax
  loc_0040E0E6: inc eax
  loc_0040E0E7: neg eax
  loc_0040E0E9: mov var_2C4, ax
  loc_0040E0F0: lea ecx, var_CC
  loc_0040E0F6: push ecx
  loc_0040E0F7: lea edx, var_C8
  loc_0040E0FD: push edx
  loc_0040E0FE: push 00000002h
  loc_0040E100: call [00401180h] ; __vbaFreeStrList
  loc_0040E106: add esp, 0000000Ch
  loc_0040E109: movsx eax, var_2C4
  loc_0040E110: test eax, eax
  loc_0040E112: jz 0040E1E0h
  loc_0040E118: mov var_160, 80020004h
  loc_0040E122: mov var_168, 0000000Ah
  loc_0040E12C: mov var_150, 80020004h
  loc_0040E136: mov var_158, 0000000Ah
  loc_0040E140: mov var_260, 004050E8h ; "IMT LampElectrical Probing"
  loc_0040E14A: mov var_268, 00000008h
  loc_0040E154: lea edx, var_268
  loc_0040E15A: lea ecx, var_148
  loc_0040E160: call [004011B4h] ; __vbaVarDup
  loc_0040E166: mov var_250, 00406974h ; "No Averages parameter in recipe - needed to instruct Keithley."
  loc_0040E170: mov var_258, 00000008h
  loc_0040E17A: lea edx, var_258
  loc_0040E180: lea ecx, var_138
  loc_0040E186: call [004011B4h] ; __vbaVarDup
  loc_0040E18C: lea ecx, var_168
  loc_0040E192: push ecx
  loc_0040E193: lea edx, var_158
  loc_0040E199: push edx
  loc_0040E19A: lea eax, var_148
  loc_0040E1A0: push eax
  loc_0040E1A1: push 00000010h
  loc_0040E1A3: lea ecx, var_138
  loc_0040E1A9: push ecx
  loc_0040E1AA: call [00401084h] ; rtcMsgBox
  loc_0040E1B0: lea edx, var_168
  loc_0040E1B6: push edx
  loc_0040E1B7: lea eax, var_158
  loc_0040E1BD: push eax
  loc_0040E1BE: lea ecx, var_148
  loc_0040E1C4: push ecx
  loc_0040E1C5: lea edx, var_138
  loc_0040E1CB: push edx
  loc_0040E1CC: push 00000004h
  loc_0040E1CE: call [00401038h] ; __vbaFreeVarList
  loc_0040E1D4: add esp, 00000014h
  loc_0040E1D7: mov eax, Me
  loc_0040E1DA: mov [eax+0000005Eh], FFFFFFh
  loc_0040E1E0: mov edx, 004069F8h ; "NPLC"
  loc_0040E1E5: lea ecx, var_C8
  loc_0040E1EB: call [00401178h] ; __vbaStrCopy
  loc_0040E1F1: lea ecx, var_CC
  loc_0040E1F7: push ecx
  loc_0040E1F8: lea edx, var_C8
  loc_0040E1FE: push edx
  loc_0040E1FF: mov eax, var_C0
  loc_0040E205: mov ecx, [eax]
  loc_0040E207: mov edx, var_C0
  loc_0040E20D: push edx
  loc_0040E20E: call [ecx+0000002Ch]
  loc_0040E211: fnclex
  loc_0040E213: mov var_2C0, eax
  loc_0040E219: cmp var_2C0, 00000000h
  loc_0040E220: jge 0040E245h
  loc_0040E222: push 0000002Ch
  loc_0040E224: push 00405B8Ch
  loc_0040E229: mov eax, var_C0
  loc_0040E22F: push eax
  loc_0040E230: mov ecx, var_2C0
  loc_0040E236: push ecx
  loc_0040E237: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040E23D: mov var_3C4, eax
  loc_0040E243: jmp 0040E24Fh
  loc_0040E245: mov var_3C4, 00000000h
  loc_0040E24F: mov edx, var_CC
  loc_0040E255: push edx
  loc_0040E256: push 00000000h
  loc_0040E258: call [004010DCh] ; __vbaStrCmp
  loc_0040E25E: neg eax
  loc_0040E260: sbb eax, eax
  loc_0040E262: inc eax
  loc_0040E263: neg eax
  loc_0040E265: mov var_2C4, ax
  loc_0040E26C: lea eax, var_CC
  loc_0040E272: push eax
  loc_0040E273: lea ecx, var_C8
  loc_0040E279: push ecx
  loc_0040E27A: push 00000002h
  loc_0040E27C: call [00401180h] ; __vbaFreeStrList
  loc_0040E282: add esp, 0000000Ch
  loc_0040E285: movsx edx, var_2C4
  loc_0040E28C: test edx, edx
  loc_0040E28E: jz 0040E35Ch
  loc_0040E294: mov var_160, 80020004h
  loc_0040E29E: mov var_168, 0000000Ah
  loc_0040E2A8: mov var_150, 80020004h
  loc_0040E2B2: mov var_158, 0000000Ah
  loc_0040E2BC: mov var_260, 004050E8h ; "IMT LampElectrical Probing"
  loc_0040E2C6: mov var_268, 00000008h
  loc_0040E2D0: lea edx, var_268
  loc_0040E2D6: lea ecx, var_148
  loc_0040E2DC: call [004011B4h] ; __vbaVarDup
  loc_0040E2E2: mov var_250, 00406A08h ; "No NPLC parameter in recipe - needed to instruct Keithley."
  loc_0040E2EC: mov var_258, 00000008h
  loc_0040E2F6: lea edx, var_258
  loc_0040E2FC: lea ecx, var_138
  loc_0040E302: call [004011B4h] ; __vbaVarDup
  loc_0040E308: lea eax, var_168
  loc_0040E30E: push eax
  loc_0040E30F: lea ecx, var_158
  loc_0040E315: push ecx
  loc_0040E316: lea edx, var_148
  loc_0040E31C: push edx
  loc_0040E31D: push 00000010h
  loc_0040E31F: lea eax, var_138
  loc_0040E325: push eax
  loc_0040E326: call [00401084h] ; rtcMsgBox
  loc_0040E32C: lea ecx, var_168
  loc_0040E332: push ecx
  loc_0040E333: lea edx, var_158
  loc_0040E339: push edx
  loc_0040E33A: lea eax, var_148
  loc_0040E340: push eax
  loc_0040E341: lea ecx, var_138
  loc_0040E347: push ecx
  loc_0040E348: push 00000004h
  loc_0040E34A: call [00401038h] ; __vbaFreeVarList
  loc_0040E350: add esp, 00000014h
  loc_0040E353: mov edx, Me
  loc_0040E356: mov [edx+0000005Eh], FFFFFFh
  loc_0040E35C: mov edx, 00406844h ; "Iterations"
  loc_0040E361: lea ecx, var_C8
  loc_0040E367: call [00401178h] ; __vbaStrCopy
  loc_0040E36D: lea eax, var_CC
  loc_0040E373: push eax
  loc_0040E374: lea ecx, var_C8
  loc_0040E37A: push ecx
  loc_0040E37B: mov edx, var_C0
  loc_0040E381: mov eax, [edx]
  loc_0040E383: mov ecx, var_C0
  loc_0040E389: push ecx
  loc_0040E38A: call [eax+0000002Ch]
  loc_0040E38D: fnclex
  loc_0040E38F: mov var_2C0, eax
  loc_0040E395: cmp var_2C0, 00000000h
  loc_0040E39C: jge 0040E3C1h
  loc_0040E39E: push 0000002Ch
  loc_0040E3A0: push 00405B8Ch
  loc_0040E3A5: mov edx, var_C0
  loc_0040E3AB: push edx
  loc_0040E3AC: mov eax, var_2C0
  loc_0040E3B2: push eax
  loc_0040E3B3: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040E3B9: mov var_3C8, eax
  loc_0040E3BF: jmp 0040E3CBh
  loc_0040E3C1: mov var_3C8, 00000000h
  loc_0040E3CB: mov ecx, var_CC
  loc_0040E3D1: push ecx
  loc_0040E3D2: call [0040117Ch] ; __vbaI4Str
  loc_0040E3D8: mov var_74, eax
  loc_0040E3DB: lea edx, var_CC
  loc_0040E3E1: push edx
  loc_0040E3E2: lea eax, var_C8
  loc_0040E3E8: push eax
  loc_0040E3E9: push 00000002h
  loc_0040E3EB: call [00401180h] ; __vbaFreeStrList
  loc_0040E3F1: add esp, 0000000Ch
  loc_0040E3F4: movsx ecx, var_18
  loc_0040E3F8: cmp ecx, 00000002h
  loc_0040E3FB: jz 0040E40Ch
  loc_0040E3FD: mov edx, Me
  loc_0040E400: movsx eax, [edx+0000005Eh]
  loc_0040E404: test eax, eax
  loc_0040E406: jz 0040E514h
  loc_0040E40C: push 00405B8Ch
  loc_0040E411: push 00000000h
  loc_0040E413: call [004011D4h] ; __vbaCastObj
  loc_0040E419: push eax
  loc_0040E41A: lea ecx, var_C0
  loc_0040E420: push ecx
  loc_0040E421: call [00401080h] ; __vbaObjSet
  loc_0040E427: mov edx, Me
  loc_0040E42A: mov eax, [edx]
  loc_0040E42C: mov ecx, Me
  loc_0040E42F: push ecx
  loc_0040E430: call [eax+0000039Ch]
  loc_0040E436: push eax
  loc_0040E437: lea edx, var_118
  loc_0040E43D: push edx
  loc_0040E43E: call [00401080h] ; __vbaObjSet
  loc_0040E444: mov var_2C0, eax
  loc_0040E44A: push 00406380h ; "Ready"
  loc_0040E44F: mov eax, var_2C0
  loc_0040E455: mov ecx, [eax]
  loc_0040E457: mov edx, var_2C0
  loc_0040E45D: push edx
  loc_0040E45E: call [ecx+00000054h]
  loc_0040E461: fnclex
  loc_0040E463: mov var_2C4, eax
  loc_0040E469: cmp var_2C4, 00000000h
  loc_0040E470: jge 0040E495h
  loc_0040E472: push 00000054h
  loc_0040E474: push 0040575Ch
  loc_0040E479: mov eax, var_2C0
  loc_0040E47F: push eax
  loc_0040E480: mov ecx, var_2C4
  loc_0040E486: push ecx
  loc_0040E487: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040E48D: mov var_3CC, eax
  loc_0040E493: jmp 0040E49Fh
  loc_0040E495: mov var_3CC, 00000000h
  loc_0040E49F: lea ecx, var_118
  loc_0040E4A5: call [004011F0h] ; __vbaFreeObj
  loc_0040E4AB: lea edx, var_138
  loc_0040E4B1: push edx
  loc_0040E4B2: mov eax, Me
  loc_0040E4B5: mov ecx, [eax]
  loc_0040E4B7: mov edx, Me
  loc_0040E4BA: push edx
  loc_0040E4BB: call [ecx+00000704h]
  loc_0040E4C1: mov var_2C0, eax
  loc_0040E4C7: cmp var_2C0, 00000000h
  loc_0040E4CE: jge 0040E4F3h
  loc_0040E4D0: push 00000704h
  loc_0040E4D5: push 0040579Ch ; "#]=VｫoyAｷ ;ﾑs：ﾚLabel12"
  loc_0040E4DA: mov eax, Me
  loc_0040E4DD: push eax
  loc_0040E4DE: mov ecx, var_2C0
  loc_0040E4E4: push ecx
  loc_0040E4E5: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040E4EB: mov var_3D0, eax
  loc_0040E4F1: jmp 0040E4FDh
  loc_0040E4F3: mov var_3D0, 00000000h
  loc_0040E4FD: lea ecx, var_138
  loc_0040E503: call [00401020h] ; __vbaFreeVar
  loc_0040E509: call [004010A0h] ; rtcDoEvents
  loc_0040E50F: jmp 0041489Fh
  loc_0040E514: mov var_130, FFFFFFFFh
  loc_0040E51E: mov var_138, 0000000Bh
  loc_0040E528: mov edx, 00406A84h ; "SP2X0Y0"
  loc_0040E52D: lea ecx, var_CC
  loc_0040E533: call [00401178h] ; __vbaStrCopy
  loc_0040E539: mov edx, 00406454h ; "2001X"
  loc_0040E53E: lea ecx, var_C8
  loc_0040E544: call [00401178h] ; __vbaStrCopy
  loc_0040E54A: lea edx, var_138
  loc_0040E550: push edx
  loc_0040E551: lea eax, var_CC
  loc_0040E557: push eax
  loc_0040E558: lea ecx, var_C8
  loc_0040E55E: push ecx
  loc_0040E55F: lea edx, var_148
  loc_0040E565: push edx
  loc_0040E566: call 0041CA40h
  loc_0040E56B: lea edx, var_148
  loc_0040E571: lea ecx, var_84
  loc_0040E577: call [00401014h] ; __vbaVarMove
  loc_0040E57D: lea eax, var_CC
  loc_0040E583: push eax
  loc_0040E584: lea ecx, var_C8
  loc_0040E58A: push ecx
  loc_0040E58B: push 00000002h
  loc_0040E58D: call [00401180h] ; __vbaFreeStrList
  loc_0040E593: add esp, 0000000Ch
  loc_0040E596: lea ecx, var_138
  loc_0040E59C: call [00401020h] ; __vbaFreeVar
  loc_0040E5A2: lea edx, var_84
  loc_0040E5A8: push edx
  loc_0040E5A9: call [00401044h] ; __vbaStrErrVarCopy
  loc_0040E5AF: mov edx, eax
  loc_0040E5B1: lea ecx, var_C8
  loc_0040E5B7: call [004011D0h] ; __vbaStrMove
  loc_0040E5BD: push eax
  loc_0040E5BE: push 00406464h ; "MC"
  loc_0040E5C3: call [004010DCh] ; __vbaStrCmp
  loc_0040E5C9: neg eax
  loc_0040E5CB: sbb eax, eax
  loc_0040E5CD: neg eax
  loc_0040E5CF: neg eax
  loc_0040E5D1: mov var_2C0, ax
  loc_0040E5D8: lea ecx, var_C8
  loc_0040E5DE: call [004011F4h] ; __vbaFreeStr
  loc_0040E5E4: movsx eax, var_2C0
  loc_0040E5EB: test eax, eax
  loc_0040E5ED: jz 0040E7F2h
  loc_0040E5F3: mov var_160, 80020004h
  loc_0040E5FD: mov var_168, 0000000Ah
  loc_0040E607: mov var_150, 80020004h
  loc_0040E611: mov var_158, 0000000Ah
  loc_0040E61B: mov var_250, 004050E8h ; "IMT LampElectrical Probing"
  loc_0040E625: mov var_258, 00000008h
  loc_0040E62F: lea edx, var_258
  loc_0040E635: lea ecx, var_148
  loc_0040E63B: call [004011B4h] ; __vbaVarDup
  loc_0040E641: push 00406470h ; "Prober command '"
  loc_0040E646: push 00406A84h ; "SP2X0Y0"
  loc_0040E64B: call [00401050h] ; __vbaStrCat
  loc_0040E651: mov edx, eax
  loc_0040E653: lea ecx, var_C8
  loc_0040E659: call [004011D0h] ; __vbaStrMove
  loc_0040E65F: push eax
  loc_0040E660: push 00406498h ; "' failed to return 'MC', instead said:"
  loc_0040E665: call [00401050h] ; __vbaStrCat
  loc_0040E66B: mov edx, eax
  loc_0040E66D: lea ecx, var_CC
  loc_0040E673: call [004011D0h] ; __vbaStrMove
  loc_0040E679: push eax
  loc_0040E67A: push 004054D8h ; vbCrLf
  loc_0040E67F: call [00401050h] ; __vbaStrCat
  loc_0040E685: mov edx, eax
  loc_0040E687: lea ecx, var_D0
  loc_0040E68D: call [004011D0h] ; __vbaStrMove
  loc_0040E693: push eax
  loc_0040E694: lea ecx, var_84
  loc_0040E69A: push ecx
  loc_0040E69B: call [00401044h] ; __vbaStrErrVarCopy
  loc_0040E6A1: mov edx, eax
  loc_0040E6A3: lea ecx, var_D4
  loc_0040E6A9: call [004011D0h] ; __vbaStrMove
  loc_0040E6AF: push eax
  loc_0040E6B0: call [00401050h] ; __vbaStrCat
  loc_0040E6B6: mov edx, eax
  loc_0040E6B8: lea ecx, var_D8
  loc_0040E6BE: call [004011D0h] ; __vbaStrMove
  loc_0040E6C4: push eax
  loc_0040E6C5: push 004054D8h ; vbCrLf
  loc_0040E6CA: call [00401050h] ; __vbaStrCat
  loc_0040E6D0: mov edx, eax
  loc_0040E6D2: lea ecx, var_DC
  loc_0040E6D8: call [004011D0h] ; __vbaStrMove
  loc_0040E6DE: push eax
  loc_0040E6DF: push 004064ECh ; "Continue anyway?"
  loc_0040E6E4: call [00401050h] ; __vbaStrCat
  loc_0040E6EA: mov var_130, eax
  loc_0040E6F0: mov var_138, 00000008h
  loc_0040E6FA: lea edx, var_168
  loc_0040E700: push edx
  loc_0040E701: lea eax, var_158
  loc_0040E707: push eax
  loc_0040E708: lea ecx, var_148
  loc_0040E70E: push ecx
  loc_0040E70F: push 00000004h
  loc_0040E711: lea edx, var_138
  loc_0040E717: push edx
  loc_0040E718: call [00401084h] ; rtcMsgBox
  loc_0040E71E: mov ecx, eax
  loc_0040E720: call [004010ECh] ; __vbaI2I4
  loc_0040E726: mov var_18, ax
  loc_0040E72A: lea eax, var_DC
  loc_0040E730: push eax
  loc_0040E731: lea ecx, var_D8
  loc_0040E737: push ecx
  loc_0040E738: lea edx, var_D4
  loc_0040E73E: push edx
  loc_0040E73F: lea eax, var_D0
  loc_0040E745: push eax
  loc_0040E746: lea ecx, var_CC
  loc_0040E74C: push ecx
  loc_0040E74D: lea edx, var_C8
  loc_0040E753: push edx
  loc_0040E754: push 00000006h
  loc_0040E756: call [00401180h] ; __vbaFreeStrList
  loc_0040E75C: add esp, 0000001Ch
  loc_0040E75F: lea eax, var_168
  loc_0040E765: push eax
  loc_0040E766: lea ecx, var_158
  loc_0040E76C: push ecx
  loc_0040E76D: lea edx, var_148
  loc_0040E773: push edx
  loc_0040E774: lea eax, var_138
  loc_0040E77A: push eax
  loc_0040E77B: push 00000004h
  loc_0040E77D: call [00401038h] ; __vbaFreeVarList
  loc_0040E783: add esp, 00000014h
  loc_0040E786: movsx ecx, var_18
  loc_0040E78A: cmp ecx, 00000007h
  loc_0040E78D: jnz 0040E7F2h
  loc_0040E78F: lea edx, var_138
  loc_0040E795: push edx
  loc_0040E796: mov eax, Me
  loc_0040E799: mov ecx, [eax]
  loc_0040E79B: mov edx, Me
  loc_0040E79E: push edx
  loc_0040E79F: call [ecx+00000704h]
  loc_0040E7A5: mov var_2C0, eax
  loc_0040E7AB: cmp var_2C0, 00000000h
  loc_0040E7B2: jge 0040E7D7h
  loc_0040E7B4: push 00000704h
  loc_0040E7B9: push 0040579Ch ; "#]=VｫoyAｷ ;ﾑs：ﾚLabel12"
  loc_0040E7BE: mov eax, Me
  loc_0040E7C1: push eax
  loc_0040E7C2: mov ecx, var_2C0
  loc_0040E7C8: push ecx
  loc_0040E7C9: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040E7CF: mov var_3D4, eax
  loc_0040E7D5: jmp 0040E7E1h
  loc_0040E7D7: mov var_3D4, 00000000h
  loc_0040E7E1: lea ecx, var_138
  loc_0040E7E7: call [00401020h] ; __vbaFreeVar
  loc_0040E7ED: jmp 0041489Fh
  loc_0040E7F2: mov edx, Me
  loc_0040E7F5: movsx eax, [edx+0000005Eh]
  loc_0040E7F9: test eax, eax
  loc_0040E7FB: jz 0040E860h
  loc_0040E7FD: lea ecx, var_138
  loc_0040E803: push ecx
  loc_0040E804: mov edx, Me
  loc_0040E807: mov eax, [edx]
  loc_0040E809: mov ecx, Me
  loc_0040E80C: push ecx
  loc_0040E80D: call [eax+00000704h]
  loc_0040E813: mov var_2C0, eax
  loc_0040E819: cmp var_2C0, 00000000h
  loc_0040E820: jge 0040E845h
  loc_0040E822: push 00000704h
  loc_0040E827: push 0040579Ch ; "#]=VｫoyAｷ ;ﾑs：ﾚLabel12"
  loc_0040E82C: mov edx, Me
  loc_0040E82F: push edx
  loc_0040E830: mov eax, var_2C0
  loc_0040E836: push eax
  loc_0040E837: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040E83D: mov var_3D8, eax
  loc_0040E843: jmp 0040E84Fh
  loc_0040E845: mov var_3D8, 00000000h
  loc_0040E84F: lea ecx, var_138
  loc_0040E855: call [00401020h] ; __vbaFreeVar
  loc_0040E85B: jmp 0041489Fh
  loc_0040E860: push 00423024h
  loc_0040E865: call 0041DD00h
  loc_0040E86A: mov var_A0, eax
  loc_0040E870: cmp [00423010h], 00000000h
  loc_0040E877: jnz 0040E895h
  loc_0040E879: push 00423010h
  loc_0040E87E: push 004025D8h
  loc_0040E883: call [00401168h] ; __vbaNew2
  loc_0040E889: mov var_3DC, 00423010h
  loc_0040E893: jmp 0040E89Fh
  loc_0040E895: mov var_3DC, 00423010h
  loc_0040E89F: mov ecx, var_3DC
  loc_0040E8A5: mov edx, [ecx]
  loc_0040E8A7: mov eax, var_3DC
  loc_0040E8AD: mov ecx, [eax]
  loc_0040E8AF: mov eax, [ecx]
  loc_0040E8B1: push edx
  loc_0040E8B2: call [eax+00000308h]
  loc_0040E8B8: push eax
  loc_0040E8B9: lea ecx, var_118
  loc_0040E8BF: push ecx
  loc_0040E8C0: call [00401080h] ; __vbaObjSet
  loc_0040E8C6: mov var_2C0, eax
  loc_0040E8CC: lea edx, var_108
  loc_0040E8D2: push edx
  loc_0040E8D3: mov eax, var_2C0
  loc_0040E8D9: mov ecx, [eax]
  loc_0040E8DB: mov edx, var_2C0
  loc_0040E8E1: push edx
  loc_0040E8E2: call [ecx+000000A0h]
  loc_0040E8E8: fnclex
  loc_0040E8EA: mov var_2C4, eax
  loc_0040E8F0: cmp var_2C4, 00000000h
  loc_0040E8F7: jge 0040E91Fh
  loc_0040E8F9: push 000000A0h
  loc_0040E8FE: push 00405398h
  loc_0040E903: mov eax, var_2C0
  loc_0040E909: push eax
  loc_0040E90A: mov ecx, var_2C4
  loc_0040E910: push ecx
  loc_0040E911: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040E917: mov var_3E0, eax
  loc_0040E91D: jmp 0040E929h
  loc_0040E91F: mov var_3E0, 00000000h
  loc_0040E929: cmp [00423010h], 00000000h
  loc_0040E930: jnz 0040E94Eh
  loc_0040E932: push 00423010h
  loc_0040E937: push 004025D8h
  loc_0040E93C: call [00401168h] ; __vbaNew2
  loc_0040E942: mov var_3E4, 00423010h
  loc_0040E94C: jmp 0040E958h
  loc_0040E94E: mov var_3E4, 00423010h
  loc_0040E958: mov edx, var_3E4
  loc_0040E95E: mov eax, [edx]
  loc_0040E960: mov ecx, var_3E4
  loc_0040E966: mov edx, [ecx]
  loc_0040E968: mov ecx, [edx]
  loc_0040E96A: push eax
  loc_0040E96B: call [ecx+00000304h]
  loc_0040E971: push eax
  loc_0040E972: lea edx, var_11C
  loc_0040E978: push edx
  loc_0040E979: call [00401080h] ; __vbaObjSet
  loc_0040E97F: mov var_2C8, eax
  loc_0040E985: lea eax, var_110
  loc_0040E98B: push eax
  loc_0040E98C: mov ecx, var_2C8
  loc_0040E992: mov edx, [ecx]
  loc_0040E994: mov eax, var_2C8
  loc_0040E99A: push eax
  loc_0040E99B: call [edx+000000A8h]
  loc_0040E9A1: fnclex
  loc_0040E9A3: mov var_2CC, eax
  loc_0040E9A9: cmp var_2CC, 00000000h
  loc_0040E9B0: jge 0040E9D8h
  loc_0040E9B2: push 000000A8h
  loc_0040E9B7: push 004055DCh
  loc_0040E9BC: mov ecx, var_2C8
  loc_0040E9C2: push ecx
  loc_0040E9C3: mov edx, var_2CC
  loc_0040E9C9: push edx
  loc_0040E9CA: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040E9D0: mov var_3E8, eax
  loc_0040E9D6: jmp 0040E9E2h
  loc_0040E9D8: mov var_3E8, 00000000h
  loc_0040E9E2: mov edx, 00406A98h ; "Voltage"
  loc_0040E9E7: lea ecx, var_C8
  loc_0040E9ED: call [00401178h] ; __vbaStrCopy
  loc_0040E9F3: lea eax, var_CC
  loc_0040E9F9: push eax
  loc_0040E9FA: lea ecx, var_C8
  loc_0040EA00: push ecx
  loc_0040EA01: mov edx, var_C0
  loc_0040EA07: mov eax, [edx]
  loc_0040EA09: mov ecx, var_C0
  loc_0040EA0F: push ecx
  loc_0040EA10: call [eax+0000002Ch]
  loc_0040EA13: fnclex
  loc_0040EA15: mov var_2D0, eax
  loc_0040EA1B: cmp var_2D0, 00000000h
  loc_0040EA22: jge 0040EA47h
  loc_0040EA24: push 0000002Ch
  loc_0040EA26: push 00405B8Ch
  loc_0040EA2B: mov edx, var_C0
  loc_0040EA31: push edx
  loc_0040EA32: mov eax, var_2D0
  loc_0040EA38: push eax
  loc_0040EA39: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040EA3F: mov var_3EC, eax
  loc_0040EA45: jmp 0040EA51h
  loc_0040EA47: mov var_3EC, 00000000h
  loc_0040EA51: mov edx, 00406AACh ; "Delay1"
  loc_0040EA56: lea ecx, var_D0
  loc_0040EA5C: call [00401178h] ; __vbaStrCopy
  loc_0040EA62: lea ecx, var_D4
  loc_0040EA68: push ecx
  loc_0040EA69: lea edx, var_D0
  loc_0040EA6F: push edx
  loc_0040EA70: mov eax, var_C0
  loc_0040EA76: mov ecx, [eax]
  loc_0040EA78: mov edx, var_C0
  loc_0040EA7E: push edx
  loc_0040EA7F: call [ecx+0000002Ch]
  loc_0040EA82: fnclex
  loc_0040EA84: mov var_2D4, eax
  loc_0040EA8A: cmp var_2D4, 00000000h
  loc_0040EA91: jge 0040EAB6h
  loc_0040EA93: push 0000002Ch
  loc_0040EA95: push 00405B8Ch
  loc_0040EA9A: mov eax, var_C0
  loc_0040EAA0: push eax
  loc_0040EAA1: mov ecx, var_2D4
  loc_0040EAA7: push ecx
  loc_0040EAA8: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040EAAE: mov var_3F0, eax
  loc_0040EAB4: jmp 0040EAC0h
  loc_0040EAB6: mov var_3F0, 00000000h
  loc_0040EAC0: mov edx, 00406AC0h ; "Delay2"
  loc_0040EAC5: lea ecx, var_D8
  loc_0040EACB: call [00401178h] ; __vbaStrCopy
  loc_0040EAD1: lea edx, var_DC
  loc_0040EAD7: push edx
  loc_0040EAD8: lea eax, var_D8
  loc_0040EADE: push eax
  loc_0040EADF: mov ecx, var_C0
  loc_0040EAE5: mov edx, [ecx]
  loc_0040EAE7: mov eax, var_C0
  loc_0040EAED: push eax
  loc_0040EAEE: call [edx+0000002Ch]
  loc_0040EAF1: fnclex
  loc_0040EAF3: mov var_2D8, eax
  loc_0040EAF9: cmp var_2D8, 00000000h
  loc_0040EB00: jge 0040EB25h
  loc_0040EB02: push 0000002Ch
  loc_0040EB04: push 00405B8Ch
  loc_0040EB09: mov ecx, var_C0
  loc_0040EB0F: push ecx
  loc_0040EB10: mov edx, var_2D8
  loc_0040EB16: push edx
  loc_0040EB17: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040EB1D: mov var_3F4, eax
  loc_0040EB23: jmp 0040EB2Fh
  loc_0040EB25: mov var_3F4, 00000000h
  loc_0040EB2F: mov edx, 00406AD4h ; "Delay3"
  loc_0040EB34: lea ecx, var_E0
  loc_0040EB3A: call [00401178h] ; __vbaStrCopy
  loc_0040EB40: lea eax, var_E4
  loc_0040EB46: push eax
  loc_0040EB47: lea ecx, var_E0
  loc_0040EB4D: push ecx
  loc_0040EB4E: mov edx, var_C0
  loc_0040EB54: mov eax, [edx]
  loc_0040EB56: mov ecx, var_C0
  loc_0040EB5C: push ecx
  loc_0040EB5D: call [eax+0000002Ch]
  loc_0040EB60: fnclex
  loc_0040EB62: mov var_2DC, eax
  loc_0040EB68: cmp var_2DC, 00000000h
  loc_0040EB6F: jge 0040EB94h
  loc_0040EB71: push 0000002Ch
  loc_0040EB73: push 00405B8Ch
  loc_0040EB78: mov edx, var_C0
  loc_0040EB7E: push edx
  loc_0040EB7F: mov eax, var_2DC
  loc_0040EB85: push eax
  loc_0040EB86: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040EB8C: mov var_3F8, eax
  loc_0040EB92: jmp 0040EB9Eh
  loc_0040EB94: mov var_3F8, 00000000h
  loc_0040EB9E: mov edx, 00406910h ; "Averages"
  loc_0040EBA3: lea ecx, var_E8
  loc_0040EBA9: call [00401178h] ; __vbaStrCopy
  loc_0040EBAF: lea ecx, var_EC
  loc_0040EBB5: push ecx
  loc_0040EBB6: lea edx, var_E8
  loc_0040EBBC: push edx
  loc_0040EBBD: mov eax, var_C0
  loc_0040EBC3: mov ecx, [eax]
  loc_0040EBC5: mov edx, var_C0
  loc_0040EBCB: push edx
  loc_0040EBCC: call [ecx+0000002Ch]
  loc_0040EBCF: fnclex
  loc_0040EBD1: mov var_2E0, eax
  loc_0040EBD7: cmp var_2E0, 00000000h
  loc_0040EBDE: jge 0040EC03h
  loc_0040EBE0: push 0000002Ch
  loc_0040EBE2: push 00405B8Ch
  loc_0040EBE7: mov eax, var_C0
  loc_0040EBED: push eax
  loc_0040EBEE: mov ecx, var_2E0
  loc_0040EBF4: push ecx
  loc_0040EBF5: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040EBFB: mov var_3FC, eax
  loc_0040EC01: jmp 0040EC0Dh
  loc_0040EC03: mov var_3FC, 00000000h
  loc_0040EC0D: mov edx, 004068A8h ; "MeterDelay"
  loc_0040EC12: lea ecx, var_F0
  loc_0040EC18: call [00401178h] ; __vbaStrCopy
  loc_0040EC1E: lea edx, var_F4
  loc_0040EC24: push edx
  loc_0040EC25: lea eax, var_F0
  loc_0040EC2B: push eax
  loc_0040EC2C: mov ecx, var_C0
  loc_0040EC32: mov edx, [ecx]
  loc_0040EC34: mov eax, var_C0
  loc_0040EC3A: push eax
  loc_0040EC3B: call [edx+0000002Ch]
  loc_0040EC3E: fnclex
  loc_0040EC40: mov var_2E4, eax
  loc_0040EC46: cmp var_2E4, 00000000h
  loc_0040EC4D: jge 0040EC72h
  loc_0040EC4F: push 0000002Ch
  loc_0040EC51: push 00405B8Ch
  loc_0040EC56: mov ecx, var_C0
  loc_0040EC5C: push ecx
  loc_0040EC5D: mov edx, var_2E4
  loc_0040EC63: push edx
  loc_0040EC64: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040EC6A: mov var_400, eax
  loc_0040EC70: jmp 0040EC7Ch
  loc_0040EC72: mov var_400, 00000000h
  loc_0040EC7C: mov edx, 00406844h ; "Iterations"
  loc_0040EC81: lea ecx, var_F8
  loc_0040EC87: call [00401178h] ; __vbaStrCopy
  loc_0040EC8D: lea eax, var_FC
  loc_0040EC93: push eax
  loc_0040EC94: lea ecx, var_F8
  loc_0040EC9A: push ecx
  loc_0040EC9B: mov edx, var_C0
  loc_0040ECA1: mov eax, [edx]
  loc_0040ECA3: mov ecx, var_C0
  loc_0040ECA9: push ecx
  loc_0040ECAA: call [eax+0000002Ch]
  loc_0040ECAD: fnclex
  loc_0040ECAF: mov var_2E8, eax
  loc_0040ECB5: cmp var_2E8, 00000000h
  loc_0040ECBC: jge 0040ECE1h
  loc_0040ECBE: push 0000002Ch
  loc_0040ECC0: push 00405B8Ch
  loc_0040ECC5: mov edx, var_C0
  loc_0040ECCB: push edx
  loc_0040ECCC: mov eax, var_2E8
  loc_0040ECD2: push eax
  loc_0040ECD3: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040ECD9: mov var_404, eax
  loc_0040ECDF: jmp 0040ECEBh
  loc_0040ECE1: mov var_404, 00000000h
  loc_0040ECEB: mov edx, 004069F8h ; "NPLC"
  loc_0040ECF0: lea ecx, var_100
  loc_0040ECF6: call [00401178h] ; __vbaStrCopy
  loc_0040ECFC: lea ecx, var_104
  loc_0040ED02: push ecx
  loc_0040ED03: lea edx, var_100
  loc_0040ED09: push edx
  loc_0040ED0A: mov eax, var_C0
  loc_0040ED10: mov ecx, [eax]
  loc_0040ED12: mov edx, var_C0
  loc_0040ED18: push edx
  loc_0040ED19: call [ecx+0000002Ch]
  loc_0040ED1C: fnclex
  loc_0040ED1E: mov var_2EC, eax
  loc_0040ED24: cmp var_2EC, 00000000h
  loc_0040ED2B: jge 0040ED50h
  loc_0040ED2D: push 0000002Ch
  loc_0040ED2F: push 00405B8Ch
  loc_0040ED34: mov eax, var_C0
  loc_0040ED3A: push eax
  loc_0040ED3B: mov ecx, var_2EC
  loc_0040ED41: push ecx
  loc_0040ED42: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040ED48: mov var_408, eax
  loc_0040ED4E: jmp 0040ED5Ah
  loc_0040ED50: mov var_408, 00000000h
  loc_0040ED5A: mov edx, var_104
  loc_0040ED60: push edx
  loc_0040ED61: call [0040117Ch] ; __vbaI4Str
  loc_0040ED67: mov var_2A4, eax
  loc_0040ED6D: mov eax, var_FC
  loc_0040ED73: push eax
  loc_0040ED74: call [0040117Ch] ; __vbaI4Str
  loc_0040ED7A: mov var_2A0, eax
  loc_0040ED80: mov ecx, var_F4
  loc_0040ED86: push ecx
  loc_0040ED87: call [00401160h] ; __vbaR8Str
  loc_0040ED8D: fstp real8 ptr var_2B4
  loc_0040ED93: mov edx, var_EC
  loc_0040ED99: push edx
  loc_0040ED9A: call [0040117Ch] ; __vbaI4Str
  loc_0040EDA0: mov var_29C, eax
  loc_0040EDA6: mov eax, var_E4
  loc_0040EDAC: push eax
  loc_0040EDAD: call [0040117Ch] ; __vbaI4Str
  loc_0040EDB3: mov var_298, eax
  loc_0040EDB9: mov ecx, var_DC
  loc_0040EDBF: push ecx
  loc_0040EDC0: call [0040117Ch] ; __vbaI4Str
  loc_0040EDC6: mov var_294, eax
  loc_0040EDCC: mov edx, var_D4
  loc_0040EDD2: push edx
  loc_0040EDD3: call [0040117Ch] ; __vbaI4Str
  loc_0040EDD9: mov var_290, eax
  loc_0040EDDF: mov eax, var_CC
  loc_0040EDE5: push eax
  loc_0040EDE6: call [00401160h] ; __vbaR8Str
  loc_0040EDEC: fstp real8 ptr var_2AC
  loc_0040EDF2: mov ecx, var_110
  loc_0040EDF8: mov var_33C, ecx
  loc_0040EDFE: mov var_110, 00000000h
  loc_0040EE08: mov edx, var_33C
  loc_0040EE0E: lea ecx, var_114
  loc_0040EE14: call [004011D0h] ; __vbaStrMove
  loc_0040EE1A: mov edx, var_108
  loc_0040EE20: mov var_340, edx
  loc_0040EE26: mov var_108, 00000000h
  loc_0040EE30: mov edx, var_340
  loc_0040EE36: lea ecx, var_10C
  loc_0040EE3C: call [004011D0h] ; __vbaStrMove
  loc_0040EE42: lea eax, var_138
  loc_0040EE48: push eax
  loc_0040EE49: lea ecx, var_2A4
  loc_0040EE4F: push ecx
  loc_0040EE50: lea edx, var_2A0
  loc_0040EE56: push edx
  loc_0040EE57: lea eax, var_2B4
  loc_0040EE5D: push eax
  loc_0040EE5E: lea ecx, var_29C
  loc_0040EE64: push ecx
  loc_0040EE65: lea edx, var_298
  loc_0040EE6B: push edx
  loc_0040EE6C: lea eax, var_294
  loc_0040EE72: push eax
  loc_0040EE73: lea ecx, var_290
  loc_0040EE79: push ecx
  loc_0040EE7A: lea edx, var_2AC
  loc_0040EE80: push edx
  loc_0040EE81: lea eax, var_114
  loc_0040EE87: push eax
  loc_0040EE88: lea ecx, var_10C
  loc_0040EE8E: push ecx
  loc_0040EE8F: lea edx, var_A0
  loc_0040EE95: push edx
  loc_0040EE96: mov eax, Me
  loc_0040EE99: mov ecx, [eax]
  loc_0040EE9B: mov edx, Me
  loc_0040EE9E: push edx
  loc_0040EE9F: call [ecx+000006FCh]
  loc_0040EEA5: mov var_2F0, eax
  loc_0040EEAB: cmp var_2F0, 00000000h
  loc_0040EEB2: jge 0040EED7h
  loc_0040EEB4: push 000006FCh
  loc_0040EEB9: push 0040579Ch ; "#]=VｫoyAｷ ;ﾑs：ﾚLabel12"
  loc_0040EEBE: mov eax, Me
  loc_0040EEC1: push eax
  loc_0040EEC2: mov ecx, var_2F0
  loc_0040EEC8: push ecx
  loc_0040EEC9: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040EECF: mov var_40C, eax
  loc_0040EED5: jmp 0040EEE1h
  loc_0040EED7: mov var_40C, 00000000h
  loc_0040EEE1: lea edx, var_114
  loc_0040EEE7: push edx
  loc_0040EEE8: lea eax, var_10C
  loc_0040EEEE: push eax
  loc_0040EEEF: lea ecx, var_104
  loc_0040EEF5: push ecx
  loc_0040EEF6: lea edx, var_100
  loc_0040EEFC: push edx
  loc_0040EEFD: lea eax, var_FC
  loc_0040EF03: push eax
  loc_0040EF04: lea ecx, var_F8
  loc_0040EF0A: push ecx
  loc_0040EF0B: lea edx, var_F4
  loc_0040EF11: push edx
  loc_0040EF12: lea eax, var_F0
  loc_0040EF18: push eax
  loc_0040EF19: lea ecx, var_EC
  loc_0040EF1F: push ecx
  loc_0040EF20: lea edx, var_E8
  loc_0040EF26: push edx
  loc_0040EF27: lea eax, var_E4
  loc_0040EF2D: push eax
  loc_0040EF2E: lea ecx, var_E0
  loc_0040EF34: push ecx
  loc_0040EF35: lea edx, var_DC
  loc_0040EF3B: push edx
  loc_0040EF3C: lea eax, var_D8
  loc_0040EF42: push eax
  loc_0040EF43: lea ecx, var_D4
  loc_0040EF49: push ecx
  loc_0040EF4A: lea edx, var_D0
  loc_0040EF50: push edx
  loc_0040EF51: lea eax, var_CC
  loc_0040EF57: push eax
  loc_0040EF58: lea ecx, var_C8
  loc_0040EF5E: push ecx
  loc_0040EF5F: push 00000012h
  loc_0040EF61: call [00401180h] ; __vbaFreeStrList
  loc_0040EF67: add esp, 0000004Ch
  loc_0040EF6A: lea edx, var_11C
  loc_0040EF70: push edx
  loc_0040EF71: lea eax, var_118
  loc_0040EF77: push eax
  loc_0040EF78: push 00000002h
  loc_0040EF7A: call [00401040h] ; __vbaFreeObjList
  loc_0040EF80: add esp, 0000000Ch
  loc_0040EF83: lea ecx, var_138
  loc_0040EF89: call [00401020h] ; __vbaFreeVar
  loc_0040EF8F: movsx ecx, [0042303Eh]
  loc_0040EF96: test ecx, ecx
  loc_0040EF98: jz 0040F304h
  loc_0040EF9E: mov var_250, 00406AE8h ; "C:\FLUSH_LampElectrical_"
  loc_0040EFA8: mov var_258, 00000008h
  loc_0040EFB2: mov edx, var_A0
  loc_0040EFB8: push edx
  loc_0040EFB9: call [00401018h] ; __vbaStrI4
  loc_0040EFBF: mov var_130, eax
  loc_0040EFC5: mov var_138, 00000008h
  loc_0040EFCF: lea eax, var_138
  loc_0040EFD5: push eax
  loc_0040EFD6: lea ecx, var_148
  loc_0040EFDC: push ecx
  loc_0040EFDD: call [004010A4h] ; rtcTrimVar
  loc_0040EFE3: mov var_260, 00406B20h ; ".SQL"
  loc_0040EFED: mov var_268, 00000008h
  loc_0040EFF7: lea edx, var_258
  loc_0040EFFD: push edx
  loc_0040EFFE: lea eax, var_148
  loc_0040F004: push eax
  loc_0040F005: lea ecx, var_158
  loc_0040F00B: push ecx
  loc_0040F00C: call [004011ACh] ; __vbaVarAdd
  loc_0040F012: push eax
  loc_0040F013: lea edx, var_268
  loc_0040F019: push edx
  loc_0040F01A: lea eax, var_168
  loc_0040F020: push eax
  loc_0040F021: call [004011ACh] ; __vbaVarAdd
  loc_0040F027: push eax
  loc_0040F028: call [00401030h] ; __vbaStrVarMove
  loc_0040F02E: mov edx, eax
  loc_0040F030: mov ecx, 00423040h
  loc_0040F035: call [004011D0h] ; __vbaStrMove
  loc_0040F03B: lea ecx, var_168
  loc_0040F041: push ecx
  loc_0040F042: lea edx, var_158
  loc_0040F048: push edx
  loc_0040F049: lea eax, var_148
  loc_0040F04F: push eax
  loc_0040F050: lea ecx, var_138
  loc_0040F056: push ecx
  loc_0040F057: push 00000004h
  loc_0040F059: call [00401038h] ; __vbaFreeVarList
  loc_0040F05F: add esp, 00000014h
  loc_0040F062: mov edx, [00423024h]
  loc_0040F068: push edx
  loc_0040F069: lea eax, var_118
  loc_0040F06F: push eax
  loc_0040F070: call [00401094h] ; __vbaObjSetAddref
  loc_0040F076: lea ecx, var_118
  loc_0040F07C: mov var_250, ecx
  loc_0040F082: mov var_258, 00004009h
  loc_0040F08C: lea edx, var_258
  loc_0040F092: push edx
  loc_0040F093: call [004010F0h] ; rtcIsObject
  loc_0040F099: mov var_28C, ax
  loc_0040F0A0: push 00406B2Ch
  loc_0040F0A5: mov eax, var_118
  loc_0040F0AB: push eax
  loc_0040F0AC: call [004011D4h] ; __vbaCastObj
  loc_0040F0B2: push eax
  loc_0040F0B3: push 00423024h
  loc_0040F0B8: call [00401080h] ; __vbaObjSet
  loc_0040F0BE: mov cx, var_28C
  loc_0040F0C5: mov var_2C0, cx
  loc_0040F0CC: lea ecx, var_118
  loc_0040F0D2: call [004011F0h] ; __vbaFreeObj
  loc_0040F0D8: movsx edx, var_2C0
  loc_0040F0DF: test edx, edx
  loc_0040F0E1: jz 0040F1B3h
  loc_0040F0E7: lea eax, var_290
  loc_0040F0ED: push eax
  loc_0040F0EE: mov ecx, [00423024h]
  loc_0040F0F4: mov edx, [ecx]
  loc_0040F0F6: mov eax, [00423024h]
  loc_0040F0FB: push eax
  loc_0040F0FC: call [edx+00000088h]
  loc_0040F102: fnclex
  loc_0040F104: mov var_2C0, eax
  loc_0040F10A: cmp var_2C0, 00000000h
  loc_0040F111: jge 0040F139h
  loc_0040F113: push 00000088h
  loc_0040F118: push 00406924h
  loc_0040F11D: mov ecx, [00423024h]
  loc_0040F123: push ecx
  loc_0040F124: mov edx, var_2C0
  loc_0040F12A: push edx
  loc_0040F12B: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040F131: mov var_410, eax
  loc_0040F137: jmp 0040F143h
  loc_0040F139: mov var_410, 00000000h
  loc_0040F143: cmp var_290, 00000001h
  loc_0040F14A: jnz 0040F19Ah
  loc_0040F14C: mov eax, [00423024h]
  loc_0040F151: mov ecx, [eax]
  loc_0040F153: mov edx, [00423024h]
  loc_0040F159: push edx
  loc_0040F15A: call [ecx+0000003Ch]
  loc_0040F15D: fnclex
  loc_0040F15F: mov var_2C0, eax
  loc_0040F165: cmp var_2C0, 00000000h
  loc_0040F16C: jge 0040F190h
  loc_0040F16E: push 0000003Ch
  loc_0040F170: push 00406924h
  loc_0040F175: mov eax, [00423024h]
  loc_0040F17A: push eax
  loc_0040F17B: mov ecx, var_2C0
  loc_0040F181: push ecx
  loc_0040F182: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040F188: mov var_414, eax
  loc_0040F18E: jmp 0040F19Ah
  loc_0040F190: mov var_414, 00000000h
  loc_0040F19A: push 00406B2Ch
  loc_0040F19F: push 00000000h
  loc_0040F1A1: call [004011D4h] ; __vbaCastObj
  loc_0040F1A7: push eax
  loc_0040F1A8: push 00423024h
  loc_0040F1AD: call [00401080h] ; __vbaObjSet
  loc_0040F1B3: mov edx, [00423028h]
  loc_0040F1B9: push edx
  loc_0040F1BA: lea eax, var_118
  loc_0040F1C0: push eax
  loc_0040F1C1: call [00401094h] ; __vbaObjSetAddref
  loc_0040F1C7: lea ecx, var_118
  loc_0040F1CD: mov var_250, ecx
  loc_0040F1D3: mov var_258, 00004009h
  loc_0040F1DD: lea edx, var_258
  loc_0040F1E3: push edx
  loc_0040F1E4: call [004010F0h] ; rtcIsObject
  loc_0040F1EA: mov var_28C, ax
  loc_0040F1F1: push 00406B2Ch
  loc_0040F1F6: mov eax, var_118
  loc_0040F1FC: push eax
  loc_0040F1FD: call [004011D4h] ; __vbaCastObj
  loc_0040F203: push eax
  loc_0040F204: push 00423028h
  loc_0040F209: call [00401080h] ; __vbaObjSet
  loc_0040F20F: mov cx, var_28C
  loc_0040F216: mov var_2C0, cx
  loc_0040F21D: lea ecx, var_118
  loc_0040F223: call [004011F0h] ; __vbaFreeObj
  loc_0040F229: movsx edx, var_2C0
  loc_0040F230: test edx, edx
  loc_0040F232: jz 0040F304h
  loc_0040F238: lea eax, var_290
  loc_0040F23E: push eax
  loc_0040F23F: mov ecx, [00423028h]
  loc_0040F245: mov edx, [ecx]
  loc_0040F247: mov eax, [00423028h]
  loc_0040F24C: push eax
  loc_0040F24D: call [edx+00000088h]
  loc_0040F253: fnclex
  loc_0040F255: mov var_2C0, eax
  loc_0040F25B: cmp var_2C0, 00000000h
  loc_0040F262: jge 0040F28Ah
  loc_0040F264: push 00000088h
  loc_0040F269: push 00406924h
  loc_0040F26E: mov ecx, [00423028h]
  loc_0040F274: push ecx
  loc_0040F275: mov edx, var_2C0
  loc_0040F27B: push edx
  loc_0040F27C: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040F282: mov var_418, eax
  loc_0040F288: jmp 0040F294h
  loc_0040F28A: mov var_418, 00000000h
  loc_0040F294: cmp var_290, 00000001h
  loc_0040F29B: jnz 0040F2EBh
  loc_0040F29D: mov eax, [00423028h]
  loc_0040F2A2: mov ecx, [eax]
  loc_0040F2A4: mov edx, [00423028h]
  loc_0040F2AA: push edx
  loc_0040F2AB: call [ecx+0000003Ch]
  loc_0040F2AE: fnclex
  loc_0040F2B0: mov var_2C0, eax
  loc_0040F2B6: cmp var_2C0, 00000000h
  loc_0040F2BD: jge 0040F2E1h
  loc_0040F2BF: push 0000003Ch
  loc_0040F2C1: push 00406924h
  loc_0040F2C6: mov eax, [00423028h]
  loc_0040F2CB: push eax
  loc_0040F2CC: mov ecx, var_2C0
  loc_0040F2D2: push ecx
  loc_0040F2D3: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040F2D9: mov var_41C, eax
  loc_0040F2DF: jmp 0040F2EBh
  loc_0040F2E1: mov var_41C, 00000000h
  loc_0040F2EB: push 00406B2Ch
  loc_0040F2F0: push 00000000h
  loc_0040F2F2: call [004011D4h] ; __vbaCastObj
  loc_0040F2F8: push eax
  loc_0040F2F9: push 00423028h
  loc_0040F2FE: call [00401080h] ; __vbaObjSet
  loc_0040F304: mov var_48, 00000000h
  loc_0040F30B: mov var_44, 00000000h
  loc_0040F312: mov var_6C, 00000000h
  loc_0040F319: mov var_68, 00000000h
  loc_0040F320: mov edx, Me
  loc_0040F323: movsx eax, [edx+0000005Eh]
  loc_0040F327: test eax, eax
  loc_0040F329: jz 0040F38Eh
  loc_0040F32B: lea ecx, var_138
  loc_0040F331: push ecx
  loc_0040F332: mov edx, Me
  loc_0040F335: mov eax, [edx]
  loc_0040F337: mov ecx, Me
  loc_0040F33A: push ecx
  loc_0040F33B: call [eax+00000704h]
  loc_0040F341: mov var_2C0, eax
  loc_0040F347: cmp var_2C0, 00000000h
  loc_0040F34E: jge 0040F373h
  loc_0040F350: push 00000704h
  loc_0040F355: push 0040579Ch ; "#]=VｫoyAｷ ;ﾑs：ﾚLabel12"
  loc_0040F35A: mov edx, Me
  loc_0040F35D: push edx
  loc_0040F35E: mov eax, var_2C0
  loc_0040F364: push eax
  loc_0040F365: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040F36B: mov var_420, eax
  loc_0040F371: jmp 0040F37Dh
  loc_0040F373: mov var_420, 00000000h
  loc_0040F37D: lea ecx, var_138
  loc_0040F383: call [00401020h] ; __vbaFreeVar
  loc_0040F389: jmp 0041489Fh
  loc_0040F38E: mov ecx, Me
  loc_0040F391: movsx edx, [ecx+0000005Eh]
  loc_0040F395: test edx, edx
  loc_0040F397: jz 0040F3FCh
  loc_0040F399: lea eax, var_138
  loc_0040F39F: push eax
  loc_0040F3A0: mov ecx, Me
  loc_0040F3A3: mov edx, [ecx]
  loc_0040F3A5: mov eax, Me
  loc_0040F3A8: push eax
  loc_0040F3A9: call [edx+00000704h]
  loc_0040F3AF: mov var_2C0, eax
  loc_0040F3B5: cmp var_2C0, 00000000h
  loc_0040F3BC: jge 0040F3E1h
  loc_0040F3BE: push 00000704h
  loc_0040F3C3: push 0040579Ch ; "#]=VｫoyAｷ ;ﾑs：ﾚLabel12"
  loc_0040F3C8: mov ecx, Me
  loc_0040F3CB: push ecx
  loc_0040F3CC: mov edx, var_2C0
  loc_0040F3D2: push edx
  loc_0040F3D3: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040F3D9: mov var_424, eax
  loc_0040F3DF: jmp 0040F3EBh
  loc_0040F3E1: mov var_424, 00000000h
  loc_0040F3EB: lea ecx, var_138
  loc_0040F3F1: call [00401020h] ; __vbaFreeVar
  loc_0040F3F7: jmp 0041489Fh
  loc_0040F3FC: mov edx, 00406938h ; "Initializing Keithley 2400"
  loc_0040F401: lea ecx, var_C8
  loc_0040F407: call [00401178h] ; __vbaStrCopy
  loc_0040F40D: lea eax, var_138
  loc_0040F413: push eax
  loc_0040F414: lea ecx, var_C8
  loc_0040F41A: push ecx
  loc_0040F41B: mov edx, Me
  loc_0040F41E: mov eax, [edx]
  loc_0040F420: mov ecx, Me
  loc_0040F423: push ecx
  loc_0040F424: call [eax+00000700h]
  loc_0040F42A: mov var_2C0, eax
  loc_0040F430: cmp var_2C0, 00000000h
  loc_0040F437: jge 0040F45Ch
  loc_0040F439: push 00000700h
  loc_0040F43E: push 0040579Ch ; "#]=VｫoyAｷ ;ﾑs：ﾚLabel12"
  loc_0040F443: mov edx, Me
  loc_0040F446: push edx
  loc_0040F447: mov eax, var_2C0
  loc_0040F44D: push eax
  loc_0040F44E: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040F454: mov var_428, eax
  loc_0040F45A: jmp 0040F466h
  loc_0040F45C: mov var_428, 00000000h
  loc_0040F466: lea ecx, var_C8
  loc_0040F46C: call [004011F4h] ; __vbaFreeStr
  loc_0040F472: lea ecx, var_138
  loc_0040F478: call [00401020h] ; __vbaFreeVar
  loc_0040F47E: mov edx, 00406764h ; "MeterCurrentLimit"
  loc_0040F483: lea ecx, var_C8
  loc_0040F489: call [00401178h] ; __vbaStrCopy
  loc_0040F48F: lea ecx, var_CC
  loc_0040F495: push ecx
  loc_0040F496: lea edx, var_C8
  loc_0040F49C: push edx
  loc_0040F49D: mov eax, var_C0
  loc_0040F4A3: mov ecx, [eax]
  loc_0040F4A5: mov edx, var_C0
  loc_0040F4AB: push edx
  loc_0040F4AC: call [ecx+0000002Ch]
  loc_0040F4AF: fnclex
  loc_0040F4B1: mov var_2C0, eax
  loc_0040F4B7: cmp var_2C0, 00000000h
  loc_0040F4BE: jge 0040F4E3h
  loc_0040F4C0: push 0000002Ch
  loc_0040F4C2: push 00405B8Ch
  loc_0040F4C7: mov eax, var_C0
  loc_0040F4CD: push eax
  loc_0040F4CE: mov ecx, var_2C0
  loc_0040F4D4: push ecx
  loc_0040F4D5: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040F4DB: mov var_42C, eax
  loc_0040F4E1: jmp 0040F4EDh
  loc_0040F4E3: mov var_42C, 00000000h
  loc_0040F4ED: mov edx, 004060DCh ; "MeterRange"
  loc_0040F4F2: lea ecx, var_D0
  loc_0040F4F8: call [00401178h] ; __vbaStrCopy
  loc_0040F4FE: lea edx, var_D4
  loc_0040F504: push edx
  loc_0040F505: lea eax, var_D0
  loc_0040F50B: push eax
  loc_0040F50C: mov ecx, var_C0
  loc_0040F512: mov edx, [ecx]
  loc_0040F514: mov eax, var_C0
  loc_0040F51A: push eax
  loc_0040F51B: call [edx+0000002Ch]
  loc_0040F51E: fnclex
  loc_0040F520: mov var_2C4, eax
  loc_0040F526: cmp var_2C4, 00000000h
  loc_0040F52D: jge 0040F552h
  loc_0040F52F: push 0000002Ch
  loc_0040F531: push 00405B8Ch
  loc_0040F536: mov ecx, var_C0
  loc_0040F53C: push ecx
  loc_0040F53D: mov edx, var_2C4
  loc_0040F543: push edx
  loc_0040F544: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040F54A: mov var_430, eax
  loc_0040F550: jmp 0040F55Ch
  loc_0040F552: mov var_430, 00000000h
  loc_0040F55C: mov eax, var_D4
  loc_0040F562: mov var_344, eax
  loc_0040F568: mov var_D4, 00000000h
  loc_0040F572: mov edx, var_344
  loc_0040F578: lea ecx, var_DC
  loc_0040F57E: call [004011D0h] ; __vbaStrMove
  loc_0040F584: mov ecx, var_CC
  loc_0040F58A: mov var_348, ecx
  loc_0040F590: mov var_CC, 00000000h
  loc_0040F59A: mov edx, var_348
  loc_0040F5A0: lea ecx, var_D8
  loc_0040F5A6: call [004011D0h] ; __vbaStrMove
  loc_0040F5AC: lea edx, var_DC
  loc_0040F5B2: push edx
  loc_0040F5B3: lea eax, var_D8
  loc_0040F5B9: push eax
  loc_0040F5BA: lea ecx, var_138
  loc_0040F5C0: push ecx
  loc_0040F5C1: call 00420200h
  loc_0040F5C6: lea edx, var_DC
  loc_0040F5CC: push edx
  loc_0040F5CD: lea eax, var_D8
  loc_0040F5D3: push eax
  loc_0040F5D4: lea ecx, var_D0
  loc_0040F5DA: push ecx
  loc_0040F5DB: lea edx, var_C8
  loc_0040F5E1: push edx
  loc_0040F5E2: push 00000004h
  loc_0040F5E4: call [00401180h] ; __vbaFreeStrList
  loc_0040F5EA: add esp, 00000014h
  loc_0040F5ED: lea ecx, var_138
  loc_0040F5F3: call [00401020h] ; __vbaFreeVar
  loc_0040F5F9: mov eax, Me
  loc_0040F5FC: movsx ecx, [eax+0000005Eh]
  loc_0040F600: test ecx, ecx
  loc_0040F602: jz 0040F667h
  loc_0040F604: lea edx, var_138
  loc_0040F60A: push edx
  loc_0040F60B: mov eax, Me
  loc_0040F60E: mov ecx, [eax]
  loc_0040F610: mov edx, Me
  loc_0040F613: push edx
  loc_0040F614: call [ecx+00000704h]
  loc_0040F61A: mov var_2C0, eax
  loc_0040F620: cmp var_2C0, 00000000h
  loc_0040F627: jge 0040F64Ch
  loc_0040F629: push 00000704h
  loc_0040F62E: push 0040579Ch ; "#]=VｫoyAｷ ;ﾑs：ﾚLabel12"
  loc_0040F633: mov eax, Me
  loc_0040F636: push eax
  loc_0040F637: mov ecx, var_2C0
  loc_0040F63D: push ecx
  loc_0040F63E: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040F644: mov var_434, eax
  loc_0040F64A: jmp 0040F656h
  loc_0040F64C: mov var_434, 00000000h
  loc_0040F656: lea ecx, var_138
  loc_0040F65C: call [00401020h] ; __vbaFreeVar
  loc_0040F662: jmp 0041489Fh
  loc_0040F667: mov edx, 00406044h ; "Initializing Switches"
  loc_0040F66C: lea ecx, var_C8
  loc_0040F672: call [00401178h] ; __vbaStrCopy
  loc_0040F678: lea edx, var_138
  loc_0040F67E: push edx
  loc_0040F67F: lea eax, var_C8
  loc_0040F685: push eax
  loc_0040F686: mov ecx, Me
  loc_0040F689: mov edx, [ecx]
  loc_0040F68B: mov eax, Me
  loc_0040F68E: push eax
  loc_0040F68F: call [edx+00000700h]
  loc_0040F695: mov var_2C0, eax
  loc_0040F69B: cmp var_2C0, 00000000h
  loc_0040F6A2: jge 0040F6C7h
  loc_0040F6A4: push 00000700h
  loc_0040F6A9: push 0040579Ch ; "#]=VｫoyAｷ ;ﾑs：ﾚLabel12"
  loc_0040F6AE: mov ecx, Me
  loc_0040F6B1: push ecx
  loc_0040F6B2: mov edx, var_2C0
  loc_0040F6B8: push edx
  loc_0040F6B9: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040F6BF: mov var_438, eax
  loc_0040F6C5: jmp 0040F6D1h
  loc_0040F6C7: mov var_438, 00000000h
  loc_0040F6D1: lea ecx, var_C8
  loc_0040F6D7: call [004011F4h] ; __vbaFreeStr
  loc_0040F6DD: lea ecx, var_138
  loc_0040F6E3: call [00401020h] ; __vbaFreeVar
  loc_0040F6E9: lea eax, var_138
  loc_0040F6EF: push eax
  loc_0040F6F0: call 0041FE20h
  loc_0040F6F5: lea ecx, var_138
  loc_0040F6FB: call [00401020h] ; __vbaFreeVar
  loc_0040F701: mov ecx, Me
  loc_0040F704: mov edx, [ecx+00000054h]
  loc_0040F707: sub edx, 00000001h
  loc_0040F70A: jo 00414AAFh
  loc_0040F710: mov var_310, edx
  loc_0040F716: mov var_30C, 00000001h
  loc_0040F720: mov var_1C, 00000000h
  loc_0040F727: jmp 0040F73Bh
  loc_0040F729: mov eax, var_1C
  loc_0040F72C: add eax, var_30C
  loc_0040F732: jo 00414AAFh
  loc_0040F738: mov var_1C, eax
  loc_0040F73B: mov ecx, var_1C
  loc_0040F73E: cmp ecx, var_310
  loc_0040F744: jg 00410544h
  loc_0040F74A: mov edx, Me
  loc_0040F74D: movsx eax, [edx+0000005Eh]
  loc_0040F751: test eax, eax
  loc_0040F753: jz 0040F7B8h
  loc_0040F755: lea ecx, var_138
  loc_0040F75B: push ecx
  loc_0040F75C: mov edx, Me
  loc_0040F75F: mov eax, [edx]
  loc_0040F761: mov ecx, Me
  loc_0040F764: push ecx
  loc_0040F765: call [eax+00000704h]
  loc_0040F76B: mov var_2C0, eax
  loc_0040F771: cmp var_2C0, 00000000h
  loc_0040F778: jge 0040F79Dh
  loc_0040F77A: push 00000704h
  loc_0040F77F: push 0040579Ch ; "#]=VｫoyAｷ ;ﾑs：ﾚLabel12"
  loc_0040F784: mov edx, Me
  loc_0040F787: push edx
  loc_0040F788: mov eax, var_2C0
  loc_0040F78E: push eax
  loc_0040F78F: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040F795: mov var_43C, eax
  loc_0040F79B: jmp 0040F7A7h
  loc_0040F79D: mov var_43C, 00000000h
  loc_0040F7A7: lea ecx, var_138
  loc_0040F7AD: call [00401020h] ; __vbaFreeVar
  loc_0040F7B3: jmp 0041489Fh
  loc_0040F7B8: mov ecx, Me
  loc_0040F7BB: cmp [ecx+0000003Ch], 00000000h
  loc_0040F7BF: jz 0040F819h
  loc_0040F7C1: mov edx, Me
  loc_0040F7C4: mov eax, [edx+0000003Ch]
  loc_0040F7C7: cmp [eax], 0001h
  loc_0040F7CB: jnz 0040F819h
  loc_0040F7CD: mov ecx, Me
  loc_0040F7D0: mov edx, [ecx+0000003Ch]
  loc_0040F7D3: mov eax, var_1C
  loc_0040F7D6: sub eax, [edx+00000014h]
  loc_0040F7D9: mov var_2C0, eax
  loc_0040F7DF: mov ecx, Me
  loc_0040F7E2: mov edx, [ecx+0000003Ch]
  loc_0040F7E5: mov eax, var_2C0
  loc_0040F7EB: cmp eax, [edx+00000010h]
  loc_0040F7EE: jae 0040F7FCh
  loc_0040F7F0: mov var_440, 00000000h
  loc_0040F7FA: jmp 0040F808h
  loc_0040F7FC: call [004010D8h] ; __vbaGenerateBoundsError
  loc_0040F802: mov var_440, eax
  loc_0040F808: mov ecx, var_2C0
  loc_0040F80E: shl ecx, 02h
  loc_0040F811: mov var_444, ecx
  loc_0040F817: jmp 0040F825h
  loc_0040F819: call [004010D8h] ; __vbaGenerateBoundsError
  loc_0040F81F: mov var_444, eax
  loc_0040F825: mov edx, Me
  loc_0040F828: cmp [edx+00000044h], 00000000h
  loc_0040F82C: jz 0040F886h
  loc_0040F82E: mov eax, Me
  loc_0040F831: mov ecx, [eax+00000044h]
  loc_0040F834: cmp [ecx], 0001h
  loc_0040F838: jnz 0040F886h
  loc_0040F83A: mov edx, Me
  loc_0040F83D: mov eax, [edx+00000044h]
  loc_0040F840: mov ecx, var_1C
  loc_0040F843: sub ecx, [eax+00000014h]
  loc_0040F846: mov var_2C4, ecx
  loc_0040F84C: mov edx, Me
  loc_0040F84F: mov eax, [edx+00000044h]
  loc_0040F852: mov ecx, var_2C4
  loc_0040F858: cmp ecx, [eax+00000010h]
  loc_0040F85B: jae 0040F869h
  loc_0040F85D: mov var_448, 00000000h
  loc_0040F867: jmp 0040F875h
  loc_0040F869: call [004010D8h] ; __vbaGenerateBoundsError
  loc_0040F86F: mov var_448, eax
  loc_0040F875: mov edx, var_2C4
  loc_0040F87B: shl edx, 02h
  loc_0040F87E: mov var_44C, edx
  loc_0040F884: jmp 0040F892h
  loc_0040F886: call [004010D8h] ; __vbaGenerateBoundsError
  loc_0040F88C: mov var_44C, eax
  loc_0040F892: mov eax, Me
  loc_0040F895: mov ecx, [eax+0000003Ch]
  loc_0040F898: mov edx, [ecx+0000000Ch]
  loc_0040F89B: mov eax, var_444
  loc_0040F8A1: xor ecx, ecx
  loc_0040F8A3: cmp [edx+eax], 00000000h
  loc_0040F8A7: setz cl
  loc_0040F8AA: mov edx, Me
  loc_0040F8AD: mov eax, [edx+00000044h]
  loc_0040F8B0: mov edx, [eax+0000000Ch]
  loc_0040F8B3: mov eax, var_44C
  loc_0040F8B9: xor ebx, ebx
  loc_0040F8BB: cmp [edx+eax], 00000000h
  loc_0040F8BF: setz bl
  loc_0040F8C2: and ecx, ebx
  loc_0040F8C4: test ecx, ecx
  loc_0040F8C6: jnz 004100B8h
  loc_0040F8CC: lea ecx, var_48
  loc_0040F8CF: mov var_260, ecx
  loc_0040F8D5: mov var_268, 00004005h
  loc_0040F8DF: mov edx, Me
  loc_0040F8E2: mov eax, [edx+0000003Ch]
  loc_0040F8E5: push eax
  loc_0040F8E6: lea ecx, var_C4
  loc_0040F8EC: push ecx
  loc_0040F8ED: call [004011A4h] ; __vbaAryLock
  loc_0040F8F3: cmp var_C4, 00000000h
  loc_0040F8FA: jz 0040F954h
  loc_0040F8FC: mov edx, var_C4
  loc_0040F902: cmp [edx], 0001h
  loc_0040F906: jnz 0040F954h
  loc_0040F908: mov eax, var_C4
  loc_0040F90E: mov ecx, var_1C
  loc_0040F911: sub ecx, [eax+00000014h]
  loc_0040F914: mov var_2C0, ecx
  loc_0040F91A: mov edx, var_C4
  loc_0040F920: mov eax, var_2C0
  loc_0040F926: cmp eax, [edx+00000010h]
  loc_0040F929: jae 0040F937h
  loc_0040F92B: mov var_450, 00000000h
  loc_0040F935: jmp 0040F943h
  loc_0040F937: call [004010D8h] ; __vbaGenerateBoundsError
  loc_0040F93D: mov var_450, eax
  loc_0040F943: mov ecx, var_2C0
  loc_0040F949: shl ecx, 02h
  loc_0040F94C: mov var_454, ecx
  loc_0040F952: jmp 0040F960h
  loc_0040F954: call [004010D8h] ; __vbaGenerateBoundsError
  loc_0040F95A: mov var_454, eax
  loc_0040F960: mov edx, var_C4
  loc_0040F966: mov eax, [edx+0000000Ch]
  loc_0040F969: add eax, var_454
  loc_0040F96F: mov var_250, eax
  loc_0040F975: mov var_258, 00004003h
  loc_0040F97F: lea ecx, var_268
  loc_0040F985: push ecx
  loc_0040F986: lea edx, var_258
  loc_0040F98C: push edx
  loc_0040F98D: call 0041DC40h
  loc_0040F992: fstp real8 ptr var_2AC
  loc_0040F998: lea eax, var_C4
  loc_0040F99E: push eax
  loc_0040F99F: call [004011E8h] ; __vbaAryUnlock
  loc_0040F9A5: mov ecx, var_2AC
  loc_0040F9AB: mov var_54, ecx
  loc_0040F9AE: mov edx, var_2A8
  loc_0040F9B4: mov var_50, edx
  loc_0040F9B7: lea eax, var_6C
  loc_0040F9BA: mov var_260, eax
  loc_0040F9C0: mov var_268, 00004005h
  loc_0040F9CA: mov ecx, Me
  loc_0040F9CD: mov edx, [ecx+00000044h]
  loc_0040F9D0: push edx
  loc_0040F9D1: lea eax, var_C4
  loc_0040F9D7: push eax
  loc_0040F9D8: call [004011A4h] ; __vbaAryLock
  loc_0040F9DE: cmp var_C4, 00000000h
  loc_0040F9E5: jz 0040FA3Fh
  loc_0040F9E7: mov ecx, var_C4
  loc_0040F9ED: cmp [ecx], 0001h
  loc_0040F9F1: jnz 0040FA3Fh
  loc_0040F9F3: mov edx, var_C4
  loc_0040F9F9: mov eax, var_1C
  loc_0040F9FC: sub eax, [edx+00000014h]
  loc_0040F9FF: mov var_2C0, eax
  loc_0040FA05: mov ecx, var_C4
  loc_0040FA0B: mov edx, var_2C0
  loc_0040FA11: cmp edx, [ecx+00000010h]
  loc_0040FA14: jae 0040FA22h
  loc_0040FA16: mov var_458, 00000000h
  loc_0040FA20: jmp 0040FA2Eh
  loc_0040FA22: call [004010D8h] ; __vbaGenerateBoundsError
  loc_0040FA28: mov var_458, eax
  loc_0040FA2E: mov eax, var_2C0
  loc_0040FA34: shl eax, 02h
  loc_0040FA37: mov var_45C, eax
  loc_0040FA3D: jmp 0040FA4Bh
  loc_0040FA3F: call [004010D8h] ; __vbaGenerateBoundsError
  loc_0040FA45: mov var_45C, eax
  loc_0040FA4B: mov ecx, var_C4
  loc_0040FA51: mov edx, [ecx+0000000Ch]
  loc_0040FA54: add edx, var_45C
  loc_0040FA5A: mov var_250, edx
  loc_0040FA60: mov var_258, 00004003h
  loc_0040FA6A: lea eax, var_268
  loc_0040FA70: push eax
  loc_0040FA71: lea ecx, var_258
  loc_0040FA77: push ecx
  loc_0040FA78: call 0041DC40h
  loc_0040FA7D: fstp real8 ptr var_2AC
  loc_0040FA83: lea edx, var_C4
  loc_0040FA89: push edx
  loc_0040FA8A: call [004011E8h] ; __vbaAryUnlock
  loc_0040FA90: mov eax, var_2AC
  loc_0040FA96: mov var_90, eax
  loc_0040FA9C: mov ecx, var_2A8
  loc_0040FAA2: mov var_8C, ecx
  loc_0040FAA8: mov edx, Me
  loc_0040FAAB: mov eax, [edx]
  loc_0040FAAD: mov ecx, Me
  loc_0040FAB0: push ecx
  loc_0040FAB1: call [eax+0000039Ch]
  loc_0040FAB7: push eax
  loc_0040FAB8: lea edx, var_118
  loc_0040FABE: push edx
  loc_0040FABF: call [00401080h] ; __vbaObjSet
  loc_0040FAC5: mov var_2C4, eax
  loc_0040FACB: mov eax, Me
  loc_0040FACE: cmp [eax+0000004Ch], 00000000h
  loc_0040FAD2: jz 0040FB2Ch
  loc_0040FAD4: mov ecx, Me
  loc_0040FAD7: mov edx, [ecx+0000004Ch]
  loc_0040FADA: cmp [edx], 0001h
  loc_0040FADE: jnz 0040FB2Ch
  loc_0040FAE0: mov eax, Me
  loc_0040FAE3: mov ecx, [eax+0000004Ch]
  loc_0040FAE6: mov edx, var_1C
  loc_0040FAE9: sub edx, [ecx+00000014h]
  loc_0040FAEC: mov var_2C0, edx
  loc_0040FAF2: mov eax, Me
  loc_0040FAF5: mov ecx, [eax+0000004Ch]
  loc_0040FAF8: mov edx, var_2C0
  loc_0040FAFE: cmp edx, [ecx+00000010h]
  loc_0040FB01: jae 0040FB0Fh
  loc_0040FB03: mov var_460, 00000000h
  loc_0040FB0D: jmp 0040FB1Bh
  loc_0040FB0F: call [004010D8h] ; __vbaGenerateBoundsError
  loc_0040FB15: mov var_460, eax
  loc_0040FB1B: mov eax, var_2C0
  loc_0040FB21: shl eax, 02h
  loc_0040FB24: mov var_464, eax
  loc_0040FB2A: jmp 0040FB38h
  loc_0040FB2C: call [004010D8h] ; __vbaGenerateBoundsError
  loc_0040FB32: mov var_464, eax
  loc_0040FB38: push 00405FB4h ; "Moving to "
  loc_0040FB3D: mov ecx, Me
  loc_0040FB40: mov edx, [ecx+0000004Ch]
  loc_0040FB43: mov eax, [edx+0000000Ch]
  loc_0040FB46: mov ecx, var_464
  loc_0040FB4C: mov edx, [eax+ecx]
  loc_0040FB4F: push edx
  loc_0040FB50: call [00401050h] ; __vbaStrCat
  loc_0040FB56: mov edx, eax
  loc_0040FB58: lea ecx, var_C8
  loc_0040FB5E: call [004011D0h] ; __vbaStrMove
  loc_0040FB64: push eax
  loc_0040FB65: mov eax, var_2C4
  loc_0040FB6B: mov ecx, [eax]
  loc_0040FB6D: mov edx, var_2C4
  loc_0040FB73: push edx
  loc_0040FB74: call [ecx+00000054h]
  loc_0040FB77: fnclex
  loc_0040FB79: mov var_2C8, eax
  loc_0040FB7F: cmp var_2C8, 00000000h
  loc_0040FB86: jge 0040FBABh
  loc_0040FB88: push 00000054h
  loc_0040FB8A: push 0040575Ch
  loc_0040FB8F: mov eax, var_2C4
  loc_0040FB95: push eax
  loc_0040FB96: mov ecx, var_2C8
  loc_0040FB9C: push ecx
  loc_0040FB9D: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0040FBA3: mov var_468, eax
  loc_0040FBA9: jmp 0040FBB5h
  loc_0040FBAB: mov var_468, 00000000h
  loc_0040FBB5: lea ecx, var_C8
  loc_0040FBBB: call [004011F4h] ; __vbaFreeStr
  loc_0040FBC1: lea ecx, var_118
  loc_0040FBC7: call [004011F0h] ; __vbaFreeObj
  loc_0040FBCD: call [004010A0h] ; rtcDoEvents
  loc_0040FBD3: mov edx, Me
  loc_0040FBD6: cmp [edx+0000003Ch], 00000000h
  loc_0040FBDA: jz 0040FC34h
  loc_0040FBDC: mov eax, Me
  loc_0040FBDF: mov ecx, [eax+0000003Ch]
  loc_0040FBE2: cmp [ecx], 0001h
  loc_0040FBE6: jnz 0040FC34h
  loc_0040FBE8: mov edx, Me
  loc_0040FBEB: mov eax, [edx+0000003Ch]
  loc_0040FBEE: mov ecx, var_1C
  loc_0040FBF1: sub ecx, [eax+00000014h]
  loc_0040FBF4: mov var_2C0, ecx
  loc_0040FBFA: mov edx, Me
  loc_0040FBFD: mov eax, [edx+0000003Ch]
  loc_0040FC00: mov ecx, var_2C0
  loc_0040FC06: cmp ecx, [eax+00000010h]
  loc_0040FC09: jae 0040FC17h
  loc_0040FC0B: mov var_46C, 00000000h
  loc_0040FC15: jmp 0040FC23h
  loc_0040FC17: call [004010D8h] ; __vbaGenerateBoundsError
  loc_0040FC1D: mov var_46C, eax
  loc_0040FC23: mov edx, var_2C0
  loc_0040FC29: shl edx, 02h
  loc_0040FC2C: mov var_470, edx
  loc_0040FC32: jmp 0040FC40h
  loc_0040FC34: call [004010D8h] ; __vbaGenerateBoundsError
  loc_0040FC3A: mov var_470, eax
  loc_0040FC40: mov eax, Me
  loc_0040FC43: mov ecx, [eax+0000003Ch]
  loc_0040FC46: mov edx, [ecx+0000000Ch]
  loc_0040FC49: mov eax, var_470
  loc_0040FC4F: fild real4 ptr [edx+eax]
  loc_0040FC52: fstp real8 ptr var_48
  loc_0040FC55: mov ecx, Me
  loc_0040FC58: cmp [ecx+00000044h], 00000000h
  loc_0040FC5C: jz 0040FCB6h
  loc_0040FC5E: mov edx, Me
  loc_0040FC61: mov eax, [edx+00000044h]
  loc_0040FC64: cmp [eax], 0001h
  loc_0040FC68: jnz 0040FCB6h
  loc_0040FC6A: mov ecx, Me
  loc_0040FC6D: mov edx, [ecx+00000044h]
  loc_0040FC70: mov eax, var_1C
  loc_0040FC73: sub eax, [edx+00000014h]
  loc_0040FC76: mov var_2C0, eax
  loc_0040FC7C: mov ecx, Me
  loc_0040FC7F: mov edx, [ecx+00000044h]
  loc_0040FC82: mov eax, var_2C0
  loc_0040FC88: cmp eax, [edx+00000010h]
  loc_0040FC8B: jae 0040FC99h
  loc_0040FC8D: mov var_474, 00000000h
  loc_0040FC97: jmp 0040FCA5h
  loc_0040FC99: call [004010D8h] ; __vbaGenerateBoundsError
  loc_0040FC9F: mov var_474, eax
  loc_0040FCA5: mov ecx, var_2C0
  loc_0040FCAB: shl ecx, 02h
  loc_0040FCAE: mov var_478, ecx
  loc_0040FCB4: jmp 0040FCC2h
  loc_0040FCB6: call [004010D8h] ; __vbaGenerateBoundsError
  loc_0040FCBC: mov var_478, eax
  loc_0040FCC2: mov edx, Me
  loc_0040FCC5: mov eax, [edx+00000044h]
  loc_0040FCC8: mov ecx, [eax+0000000Ch]
  loc_0040FCCB: mov edx, var_478
  loc_0040FCD1: fild real4 ptr [ecx+edx]
  loc_0040FCD4: fstp real8 ptr var_6C
  loc_0040FCD7: mov var_250, 00406440h ; "MMX"
  loc_0040FCE1: mov var_258, 00000008h
  loc_0040FCEB: mov eax, var_50
  loc_0040FCEE: push eax
  loc_0040FCEF: mov ecx, var_54
  loc_0040FCF2: push ecx
  loc_0040FCF3: call [00401104h] ; __vbaStrR8
  loc_0040FCF9: mov var_130, eax
  loc_0040FCFF: mov var_138, 00000008h
  loc_0040FD09: lea edx, var_138
  loc_0040FD0F: push edx
  loc_0040FD10: lea eax, var_148
  loc_0040FD16: push eax
  loc_0040FD17: call [004010A4h] ; rtcTrimVar
  loc_0040FD1D: mov var_260, 0040644Ch ; "Y"
  loc_0040FD27: mov var_268, 00000008h
  loc_0040FD31: mov ecx, var_8C
  loc_0040FD37: push ecx
  loc_0040FD38: mov edx, var_90
  loc_0040FD3E: push edx
  loc_0040FD3F: call [00401104h] ; __vbaStrR8
  loc_0040FD45: mov var_170, eax
  loc_0040FD4B: mov var_178, 00000008h
  loc_0040FD55: lea eax, var_178
  loc_0040FD5B: push eax
  loc_0040FD5C: lea ecx, var_188
  loc_0040FD62: push ecx
  loc_0040FD63: call [004010A4h] ; rtcTrimVar
  loc_0040FD69: lea edx, var_258
  loc_0040FD6F: push edx
  loc_0040FD70: lea eax, var_148
  loc_0040FD76: push eax
  loc_0040FD77: lea ecx, var_158
  loc_0040FD7D: push ecx
  loc_0040FD7E: call [004011ACh] ; __vbaVarAdd
  loc_0040FD84: push eax
  loc_0040FD85: lea edx, var_268
  loc_0040FD8B: push edx
  loc_0040FD8C: lea eax, var_168
  loc_0040FD92: push eax
  loc_0040FD93: call [004011ACh] ; __vbaVarAdd
  loc_0040FD99: push eax
  loc_0040FD9A: lea ecx, var_188
  loc_0040FDA0: push ecx
  loc_0040FDA1: lea edx, var_198
  loc_0040FDA7: push edx
  loc_0040FDA8: call [004011ACh] ; __vbaVarAdd
  loc_0040FDAE: push eax
  loc_0040FDAF: call [00401030h] ; __vbaStrVarMove
  loc_0040FDB5: mov edx, eax
  loc_0040FDB7: lea ecx, var_58
  loc_0040FDBA: call [004011D0h] ; __vbaStrMove
  loc_0040FDC0: lea eax, var_198
  loc_0040FDC6: push eax
  loc_0040FDC7: lea ecx, var_188
  loc_0040FDCD: push ecx
  loc_0040FDCE: lea edx, var_168
  loc_0040FDD4: push edx
  loc_0040FDD5: lea eax, var_178
  loc_0040FDDB: push eax
  loc_0040FDDC: lea ecx, var_158
  loc_0040FDE2: push ecx
  loc_0040FDE3: lea edx, var_148
  loc_0040FDE9: push edx
  loc_0040FDEA: lea eax, var_138
  loc_0040FDF0: push eax
  loc_0040FDF1: push 00000007h
  loc_0040FDF3: call [00401038h] ; __vbaFreeVarList
  loc_0040FDF9: add esp, 00000020h
  loc_0040FDFC: mov var_130, FFFFFFFFh
  loc_0040FE06: mov var_138, 0000000Bh
  loc_0040FE10: mov edx, 00406454h ; "2001X"
  loc_0040FE15: lea ecx, var_C8
  loc_0040FE1B: call [00401178h] ; __vbaStrCopy
  loc_0040FE21: lea ecx, var_138
  loc_0040FE27: push ecx
  loc_0040FE28: lea edx, var_58
  loc_0040FE2B: push edx
  loc_0040FE2C: lea eax, var_C8
  loc_0040FE32: push eax
  loc_0040FE33: lea ecx, var_148
  loc_0040FE39: push ecx
  loc_0040FE3A: call 0041CA40h
  loc_0040FE3F: lea edx, var_148
  loc_0040FE45: lea ecx, var_84
  loc_0040FE4B: call [00401014h] ; __vbaVarMove
  loc_0040FE51: lea ecx, var_C8
  loc_0040FE57: call [004011F4h] ; __vbaFreeStr
  loc_0040FE5D: lea ecx, var_138
  loc_0040FE63: call [00401020h] ; __vbaFreeVar
  loc_0040FE69: lea edx, var_84
  loc_0040FE6F: push edx
  loc_0040FE70: call [00401044h] ; __vbaStrErrVarCopy
  loc_0040FE76: mov edx, eax
  loc_0040FE78: lea ecx, var_C8
  loc_0040FE7E: call [004011D0h] ; __vbaStrMove
  loc_0040FE84: push eax
  loc_0040FE85: push 00406464h ; "MC"
  loc_0040FE8A: call [004010DCh] ; __vbaStrCmp
  loc_0040FE90: neg eax
  loc_0040FE92: sbb eax, eax
  loc_0040FE94: neg eax
  loc_0040FE96: neg eax
  loc_0040FE98: mov var_2C0, ax
  loc_0040FE9F: lea ecx, var_C8
  loc_0040FEA5: call [004011F4h] ; __vbaFreeStr
  loc_0040FEAB: movsx eax, var_2C0
  loc_0040FEB2: test eax, eax
  loc_0040FEB4: jz 004100B8h
  loc_0040FEBA: mov var_160, 80020004h
  loc_0040FEC4: mov var_168, 0000000Ah
  loc_0040FECE: mov var_150, 80020004h
  loc_0040FED8: mov var_158, 0000000Ah
  loc_0040FEE2: mov var_250, 004050E8h ; "IMT LampElectrical Probing"
  loc_0040FEEC: mov var_258, 00000008h
  loc_0040FEF6: lea edx, var_258
  loc_0040FEFC: lea ecx, var_148
  loc_0040FF02: call [004011B4h] ; __vbaVarDup
  loc_0040FF08: push 00406470h ; "Prober command '"
  loc_0040FF0D: mov ecx, var_58
  loc_0040FF10: push ecx
  loc_0040FF11: call [00401050h] ; __vbaStrCat
  loc_0040FF17: mov edx, eax
  loc_0040FF19: lea ecx, var_C8
  loc_0040FF1F: call [004011D0h] ; __vbaStrMove
  loc_0040FF25: push eax
  loc_0040FF26: push 00406498h ; "' failed to return 'MC', instead said:"
  loc_0040FF2B: call [00401050h] ; __vbaStrCat
  loc_0040FF31: mov edx, eax
  loc_0040FF33: lea ecx, var_CC
  loc_0040FF39: call [004011D0h] ; __vbaStrMove
  loc_0040FF3F: push eax
  loc_0040FF40: push 004054D8h ; vbCrLf
  loc_0040FF45: call [00401050h] ; __vbaStrCat
  loc_0040FF4B: mov edx, eax
  loc_0040FF4D: lea ecx, var_D0
  loc_0040FF53: call [004011D0h] ; __vbaStrMove
  loc_0040FF59: push eax
  loc_0040FF5A: lea edx, var_84
  loc_0040FF60: push edx
  loc_0040FF61: call [00401044h] ; __vbaStrErrVarCopy
  loc_0040FF67: mov edx, eax
  loc_0040FF69: lea ecx, var_D4
  loc_0040FF6F: call [004011D0h] ; __vbaStrMove
  loc_0040FF75: push eax
  loc_0040FF76: call [00401050h] ; __vbaStrCat
  loc_0040FF7C: mov edx, eax
  loc_0040FF7E: lea ecx, var_D8
  loc_0040FF84: call [004011D0h] ; __vbaStrMove
  loc_0040FF8A: push eax
  loc_0040FF8B: push 004054D8h ; vbCrLf
  loc_0040FF90: call [00401050h] ; __vbaStrCat
  loc_0040FF96: mov edx, eax
  loc_0040FF98: lea ecx, var_DC
  loc_0040FF9E: call [004011D0h] ; __vbaStrMove
  loc_0040FFA4: push eax
  loc_0040FFA5: push 004064ECh ; "Continue anyway?"
  loc_0040FFAA: call [00401050h] ; __vbaStrCat
  loc_0040FFB0: mov var_130, eax
  loc_0040FFB6: mov var_138, 00000008h
  loc_0040FFC0: lea eax, var_168
  loc_0040FFC6: push eax
  loc_0040FFC7: lea ecx, var_158
  loc_0040FFCD: push ecx
  loc_0040FFCE: lea edx, var_148
  loc_0040FFD4: push edx
  loc_0040FFD5: push 00000004h
  loc_0040FFD7: lea eax, var_138
  loc_0040FFDD: push eax
  loc_0040FFDE: call [00401084h] ; rtcMsgBox
  loc_0040FFE4: mov ecx, eax
  loc_0040FFE6: call [004010ECh] ; __vbaI2I4
  loc_0040FFEC: mov var_18, ax
  loc_0040FFF0: lea ecx, var_DC
  loc_0040FFF6: push ecx
  loc_0040FFF7: lea edx, var_D8
  loc_0040FFFD: push edx
  loc_0040FFFE: lea eax, var_D4
  loc_00410004: push eax
  loc_00410005: lea ecx, var_D0
  loc_0041000B: push ecx
  loc_0041000C: lea edx, var_CC
  loc_00410012: push edx
  loc_00410013: lea eax, var_C8
  loc_00410019: push eax
  loc_0041001A: push 00000006h
  loc_0041001C: call [00401180h] ; __vbaFreeStrList
  loc_00410022: add esp, 0000001Ch
  loc_00410025: lea ecx, var_168
  loc_0041002B: push ecx
  loc_0041002C: lea edx, var_158
  loc_00410032: push edx
  loc_00410033: lea eax, var_148
  loc_00410039: push eax
  loc_0041003A: lea ecx, var_138
  loc_00410040: push ecx
  loc_00410041: push 00000004h
  loc_00410043: call [00401038h] ; __vbaFreeVarList
  loc_00410049: add esp, 00000014h
  loc_0041004C: movsx edx, var_18
  loc_00410050: cmp edx, 00000007h
  loc_00410053: jnz 004100B8h
  loc_00410055: lea eax, var_138
  loc_0041005B: push eax
  loc_0041005C: mov ecx, Me
  loc_0041005F: mov edx, [ecx]
  loc_00410061: mov eax, Me
  loc_00410064: push eax
  loc_00410065: call [edx+00000704h]
  loc_0041006B: mov var_2C0, eax
  loc_00410071: cmp var_2C0, 00000000h
  loc_00410078: jge 0041009Dh
  loc_0041007A: push 00000704h
  loc_0041007F: push 0040579Ch ; "#]=VｫoyAｷ ;ﾑs：ﾚLabel12"
  loc_00410084: mov ecx, Me
  loc_00410087: push ecx
  loc_00410088: mov edx, var_2C0
  loc_0041008E: push edx
  loc_0041008F: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00410095: mov var_47C, eax
  loc_0041009B: jmp 004100A7h
  loc_0041009D: mov var_47C, 00000000h
  loc_004100A7: lea ecx, var_138
  loc_004100AD: call [00401020h] ; __vbaFreeVar
  loc_004100B3: jmp 0041489Fh
  loc_004100B8: mov eax, Me
  loc_004100BB: cmp [eax+0000004Ch], 00000000h
  loc_004100BF: jz 00410119h
  loc_004100C1: mov ecx, Me
  loc_004100C4: mov edx, [ecx+0000004Ch]
  loc_004100C7: cmp [edx], 0001h
  loc_004100CB: jnz 00410119h
  loc_004100CD: mov eax, Me
  loc_004100D0: mov ecx, [eax+0000004Ch]
  loc_004100D3: mov edx, var_1C
  loc_004100D6: sub edx, [ecx+00000014h]
  loc_004100D9: mov var_2C0, edx
  loc_004100DF: mov eax, Me
  loc_004100E2: mov ecx, [eax+0000004Ch]
  loc_004100E5: mov edx, var_2C0
  loc_004100EB: cmp edx, [ecx+00000010h]
  loc_004100EE: jae 004100FCh
  loc_004100F0: mov var_480, 00000000h
  loc_004100FA: jmp 00410108h
  loc_004100FC: call [004010D8h] ; __vbaGenerateBoundsError
  loc_00410102: mov var_480, eax
  loc_00410108: mov eax, var_2C0
  loc_0041010E: shl eax, 02h
  loc_00410111: mov var_484, eax
  loc_00410117: jmp 00410125h
  loc_00410119: call [004010D8h] ; __vbaGenerateBoundsError
  loc_0041011F: mov var_484, eax
  loc_00410125: mov ecx, Me
  loc_00410128: mov edx, [ecx+0000004Ch]
  loc_0041012B: mov eax, [edx+0000000Ch]
  loc_0041012E: mov ecx, var_484
  loc_00410134: mov edx, [eax+ecx]
  loc_00410137: lea ecx, var_40
  loc_0041013A: call [00401178h] ; __vbaStrCopy
  loc_00410140: mov edx, Me
  loc_00410143: movsx eax, [edx+0000005Eh]
  loc_00410147: test eax, eax
  loc_00410149: jz 00410217h
  loc_0041014F: lea ecx, var_138
  loc_00410155: push ecx
  loc_00410156: lea edx, var_A0
  loc_0041015C: push edx
  loc_0041015D: mov eax, Me
  loc_00410160: mov ecx, [eax]
  loc_00410162: mov edx, Me
  loc_00410165: push edx
  loc_00410166: call [ecx+00000708h]
  loc_0041016C: mov var_2C0, eax
  loc_00410172: cmp var_2C0, 00000000h
  loc_00410179: jge 0041019Eh
  loc_0041017B: push 00000708h
  loc_00410180: push 0040579Ch ; "#]=VｫoyAｷ ;ﾑs：ﾚLabel12"
  loc_00410185: mov eax, Me
  loc_00410188: push eax
  loc_00410189: mov ecx, var_2C0
  loc_0041018F: push ecx
  loc_00410190: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00410196: mov var_488, eax
  loc_0041019C: jmp 004101A8h
  loc_0041019E: mov var_488, 00000000h
  loc_004101A8: lea ecx, var_138
  loc_004101AE: call [00401020h] ; __vbaFreeVar
  loc_004101B4: lea edx, var_138
  loc_004101BA: push edx
  loc_004101BB: mov eax, Me
  loc_004101BE: mov ecx, [eax]
  loc_004101C0: mov edx, Me
  loc_004101C3: push edx
  loc_004101C4: call [ecx+00000704h]
  loc_004101CA: mov var_2C0, eax
  loc_004101D0: cmp var_2C0, 00000000h
  loc_004101D7: jge 004101FCh
  loc_004101D9: push 00000704h
  loc_004101DE: push 0040579Ch ; "#]=VｫoyAｷ ;ﾑs：ﾚLabel12"
  loc_004101E3: mov eax, Me
  loc_004101E6: push eax
  loc_004101E7: mov ecx, var_2C0
  loc_004101ED: push ecx
  loc_004101EE: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004101F4: mov var_48C, eax
  loc_004101FA: jmp 00410206h
  loc_004101FC: mov var_48C, 00000000h
  loc_00410206: lea ecx, var_138
  loc_0041020C: call [00401020h] ; __vbaFreeVar
  loc_00410212: jmp 0041489Fh
  loc_00410217: mov edx, Me
  loc_0041021A: mov eax, [edx]
  loc_0041021C: mov ecx, Me
  loc_0041021F: push ecx
  loc_00410220: call [eax+0000039Ch]
  loc_00410226: push eax
  loc_00410227: lea edx, var_118
  loc_0041022D: push edx
  loc_0041022E: call [00401080h] ; __vbaObjSet
  loc_00410234: mov var_2C4, eax
  loc_0041023A: mov eax, Me
  loc_0041023D: cmp [eax+0000004Ch], 00000000h
  loc_00410241: jz 0041029Bh
  loc_00410243: mov ecx, Me
  loc_00410246: mov edx, [ecx+0000004Ch]
  loc_00410249: cmp [edx], 0001h
  loc_0041024D: jnz 0041029Bh
  loc_0041024F: mov eax, Me
  loc_00410252: mov ecx, [eax+0000004Ch]
  loc_00410255: mov edx, var_1C
  loc_00410258: sub edx, [ecx+00000014h]
  loc_0041025B: mov var_2C0, edx
  loc_00410261: mov eax, Me
  loc_00410264: mov ecx, [eax+0000004Ch]
  loc_00410267: mov edx, var_2C0
  loc_0041026D: cmp edx, [ecx+00000010h]
  loc_00410270: jae 0041027Eh
  loc_00410272: mov var_490, 00000000h
  loc_0041027C: jmp 0041028Ah
  loc_0041027E: call [004010D8h] ; __vbaGenerateBoundsError
  loc_00410284: mov var_490, eax
  loc_0041028A: mov eax, var_2C0
  loc_00410290: shl eax, 02h
  loc_00410293: mov var_494, eax
  loc_00410299: jmp 004102A7h
  loc_0041029B: call [004010D8h] ; __vbaGenerateBoundsError
  loc_004102A1: mov var_494, eax
  loc_004102A7: push 00406594h ; "Probing "
  loc_004102AC: mov ecx, Me
  loc_004102AF: mov edx, [ecx+0000004Ch]
  loc_004102B2: mov eax, [edx+0000000Ch]
  loc_004102B5: mov ecx, var_494
  loc_004102BB: mov edx, [eax+ecx]
  loc_004102BE: push edx
  loc_004102BF: call [00401050h] ; __vbaStrCat
  loc_004102C5: mov edx, eax
  loc_004102C7: lea ecx, var_C8
  loc_004102CD: call [004011D0h] ; __vbaStrMove
  loc_004102D3: push eax
  loc_004102D4: mov eax, var_2C4
  loc_004102DA: mov ecx, [eax]
  loc_004102DC: mov edx, var_2C4
  loc_004102E2: push edx
  loc_004102E3: call [ecx+00000054h]
  loc_004102E6: fnclex
  loc_004102E8: mov var_2C8, eax
  loc_004102EE: cmp var_2C8, 00000000h
  loc_004102F5: jge 0041031Ah
  loc_004102F7: push 00000054h
  loc_004102F9: push 0040575Ch
  loc_004102FE: mov eax, var_2C4
  loc_00410304: push eax
  loc_00410305: mov ecx, var_2C8
  loc_0041030B: push ecx
  loc_0041030C: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00410312: mov var_498, eax
  loc_00410318: jmp 00410324h
  loc_0041031A: mov var_498, 00000000h
  loc_00410324: lea ecx, var_C8
  loc_0041032A: call [004011F4h] ; __vbaFreeStr
  loc_00410330: lea ecx, var_118
  loc_00410336: call [004011F0h] ; __vbaFreeObj
  loc_0041033C: mov edx, Me
  loc_0041033F: cmp [edx+0000004Ch], 00000000h
  loc_00410343: jz 0041039Dh
  loc_00410345: mov eax, Me
  loc_00410348: mov ecx, [eax+0000004Ch]
  loc_0041034B: cmp [ecx], 0001h
  loc_0041034F: jnz 0041039Dh
  loc_00410351: mov edx, Me
  loc_00410354: mov eax, [edx+0000004Ch]
  loc_00410357: mov ecx, var_1C
  loc_0041035A: sub ecx, [eax+00000014h]
  loc_0041035D: mov var_2C0, ecx
  loc_00410363: mov edx, Me
  loc_00410366: mov eax, [edx+0000004Ch]
  loc_00410369: mov ecx, var_2C0
  loc_0041036F: cmp ecx, [eax+00000010h]
  loc_00410372: jae 00410380h
  loc_00410374: mov var_49C, 00000000h
  loc_0041037E: jmp 0041038Ch
  loc_00410380: call [004010D8h] ; __vbaGenerateBoundsError
  loc_00410386: mov var_49C, eax
  loc_0041038C: mov edx, var_2C0
  loc_00410392: shl edx, 02h
  loc_00410395: mov var_4A0, edx
  loc_0041039B: jmp 004103A9h
  loc_0041039D: call [004010D8h] ; __vbaGenerateBoundsError
  loc_004103A3: mov var_4A0, eax
  loc_004103A9: push 00405DB0h ; "Measuring "
  loc_004103AE: mov eax, Me
  loc_004103B1: mov ecx, [eax+0000004Ch]
  loc_004103B4: mov edx, [ecx+0000000Ch]
  loc_004103B7: mov eax, var_4A0
  loc_004103BD: mov ecx, [edx+eax]
  loc_004103C0: push ecx
  loc_004103C1: call [00401050h] ; __vbaStrCat
  loc_004103C7: mov edx, eax
  loc_004103C9: lea ecx, var_C8
  loc_004103CF: call [004011D0h] ; __vbaStrMove
  loc_004103D5: lea edx, var_138
  loc_004103DB: push edx
  loc_004103DC: lea eax, var_C8
  loc_004103E2: push eax
  loc_004103E3: mov ecx, Me
  loc_004103E6: mov edx, [ecx]
  loc_004103E8: mov eax, Me
  loc_004103EB: push eax
  loc_004103EC: call [edx+00000700h]
  loc_004103F2: mov var_2C4, eax
  loc_004103F8: cmp var_2C4, 00000000h
  loc_004103FF: jge 00410424h
  loc_00410401: push 00000700h
  loc_00410406: push 0040579Ch ; "#]=VｫoyAｷ ;ﾑs：ﾚLabel12"
  loc_0041040B: mov ecx, Me
  loc_0041040E: push ecx
  loc_0041040F: mov edx, var_2C4
  loc_00410415: push edx
  loc_00410416: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041041C: mov var_4A4, eax
  loc_00410422: jmp 0041042Eh
  loc_00410424: mov var_4A4, 00000000h
  loc_0041042E: lea ecx, var_C8
  loc_00410434: call [004011F4h] ; __vbaFreeStr
  loc_0041043A: lea ecx, var_138
  loc_00410440: call [00401020h] ; __vbaFreeVar
  loc_00410446: lea eax, var_314
  loc_0041044C: push eax
  loc_0041044D: call [00401138h] ; __vbaGosub
  loc_00410453: test eax, eax
  loc_00410455: jnz 0041045Ch
  loc_00410457: jmp 0041302Ch
  loc_0041045C: xor ecx, ecx
  loc_0041045E: test ecx, ecx
  loc_00410460: jz 0041053Fh
  loc_00410466: mov var_160, 80020004h
  loc_00410470: mov var_168, 0000000Ah
  loc_0041047A: mov var_150, 80020004h
  loc_00410484: mov var_158, 0000000Ah
  loc_0041048E: mov var_260, 004050E8h ; "IMT LampElectrical Probing"
  loc_00410498: mov var_268, 00000008h
  loc_004104A2: lea edx, var_268
  loc_004104A8: lea ecx, var_148
  loc_004104AE: call [004011B4h] ; __vbaVarDup
  loc_004104B4: mov var_250, 00406B40h ; "Continue?"
  loc_004104BE: mov var_258, 00000008h
  loc_004104C8: lea edx, var_258
  loc_004104CE: lea ecx, var_138
  loc_004104D4: call [004011B4h] ; __vbaVarDup
  loc_004104DA: lea edx, var_168
  loc_004104E0: push edx
  loc_004104E1: lea eax, var_158
  loc_004104E7: push eax
  loc_004104E8: lea ecx, var_148
  loc_004104EE: push ecx
  loc_004104EF: push 00000004h
  loc_004104F1: lea edx, var_138
  loc_004104F7: push edx
  loc_004104F8: call [00401084h] ; rtcMsgBox
  loc_004104FE: mov ecx, eax
  loc_00410500: call [004010ECh] ; __vbaI2I4
  loc_00410506: mov var_18, ax
  loc_0041050A: lea eax, var_168
  loc_00410510: push eax
  loc_00410511: lea ecx, var_158
  loc_00410517: push ecx
  loc_00410518: lea edx, var_148
  loc_0041051E: push edx
  loc_0041051F: lea eax, var_138
  loc_00410525: push eax
  loc_00410526: push 00000004h
  loc_00410528: call [00401038h] ; __vbaFreeVarList
  loc_0041052E: add esp, 00000014h
  loc_00410531: movsx ecx, var_18
  loc_00410535: cmp ecx, 00000007h
  loc_00410538: jnz 0041053Fh
  loc_0041053A: jmp 0041489Fh
  loc_0041053F: jmp 0040F729h
  loc_00410544: mov var_2BC, 00000000h
  loc_0041054E: mov var_2B8, 00000000h
  loc_00410558: mov var_2B4, 00000000h
  loc_00410562: mov var_2B0, 00000000h
  loc_0041056C: mov var_2AC, 00000000h
  loc_00410576: mov var_2A8, 00000000h
  loc_00410580: mov var_298, 00000000h
  loc_0041058A: mov var_294, 00000000h
  loc_00410594: mov edx, 00406B58h
  loc_00410599: lea ecx, var_C8
  loc_0041059F: call [00401178h] ; __vbaStrCopy
  loc_004105A5: mov var_290, 00000000h
  loc_004105AF: mov var_28C, FFFFFFh
  loc_004105B8: lea edx, var_2BC
  loc_004105BE: push edx
  loc_004105BF: lea eax, var_2B4
  loc_004105C5: push eax
  loc_004105C6: lea ecx, var_2AC
  loc_004105CC: push ecx
  loc_004105CD: lea edx, var_298
  loc_004105D3: push edx
  loc_004105D4: lea eax, var_294
  loc_004105DA: push eax
  loc_004105DB: lea ecx, var_C8
  loc_004105E1: push ecx
  loc_004105E2: lea edx, var_290
  loc_004105E8: push edx
  loc_004105E9: lea eax, var_28C
  loc_004105EF: push eax
  loc_004105F0: lea ecx, var_138
  loc_004105F6: push ecx
  loc_004105F7: call 0041F410h
  loc_004105FC: lea ecx, var_C8
  loc_00410602: call [004011F4h] ; __vbaFreeStr
  loc_00410608: lea ecx, var_138
  loc_0041060E: call [00401020h] ; __vbaFreeVar
  loc_00410614: mov edx, 00406B60h ; "Probing Complete"
  loc_00410619: lea ecx, var_C8
  loc_0041061F: call [00401178h] ; __vbaStrCopy
  loc_00410625: lea edx, var_138
  loc_0041062B: push edx
  loc_0041062C: lea eax, var_C8
  loc_00410632: push eax
  loc_00410633: mov ecx, Me
  loc_00410636: mov edx, [ecx]
  loc_00410638: mov eax, Me
  loc_0041063B: push eax
  loc_0041063C: call [edx+00000700h]
  loc_00410642: mov var_2C0, eax
  loc_00410648: cmp var_2C0, 00000000h
  loc_0041064F: jge 00410674h
  loc_00410651: push 00000700h
  loc_00410656: push 0040579Ch ; "#]=VｫoyAｷ ;ﾑs：ﾚLabel12"
  loc_0041065B: mov ecx, Me
  loc_0041065E: push ecx
  loc_0041065F: mov edx, var_2C0
  loc_00410665: push edx
  loc_00410666: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041066C: mov var_4A8, eax
  loc_00410672: jmp 0041067Eh
  loc_00410674: mov var_4A8, 00000000h
  loc_0041067E: lea ecx, var_C8
  loc_00410684: call [004011F4h] ; __vbaFreeStr
  loc_0041068A: lea ecx, var_138
  loc_00410690: call [00401020h] ; __vbaFreeVar
  loc_00410696: push 00405B8Ch
  loc_0041069B: push 00000000h
  loc_0041069D: call [004011D4h] ; __vbaCastObj
  loc_004106A3: push eax
  loc_004106A4: lea eax, var_C0
  loc_004106AA: push eax
  loc_004106AB: call [00401080h] ; __vbaObjSet
  loc_004106B1: mov ecx, Me
  loc_004106B4: mov edx, [ecx]
  loc_004106B6: mov eax, Me
  loc_004106B9: push eax
  loc_004106BA: call [edx+0000039Ch]
  loc_004106C0: push eax
  loc_004106C1: lea ecx, var_118
  loc_004106C7: push ecx
  loc_004106C8: call [00401080h] ; __vbaObjSet
  loc_004106CE: mov var_2C0, eax
  loc_004106D4: push 00406B88h ; "Probe Recipe completed normally"
  loc_004106D9: mov edx, var_2C0
  loc_004106DF: mov eax, [edx]
  loc_004106E1: mov ecx, var_2C0
  loc_004106E7: push ecx
  loc_004106E8: call [eax+00000054h]
  loc_004106EB: fnclex
  loc_004106ED: mov var_2C4, eax
  loc_004106F3: cmp var_2C4, 00000000h
  loc_004106FA: jge 0041071Fh
  loc_004106FC: push 00000054h
  loc_004106FE: push 0040575Ch
  loc_00410703: mov edx, var_2C0
  loc_00410709: push edx
  loc_0041070A: mov eax, var_2C4
  loc_00410710: push eax
  loc_00410711: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00410717: mov var_4AC, eax
  loc_0041071D: jmp 00410729h
  loc_0041071F: mov var_4AC, 00000000h
  loc_00410729: lea ecx, var_118
  loc_0041072F: call [004011F0h] ; __vbaFreeObj
  loc_00410735: lea ecx, var_138
  loc_0041073B: push ecx
  loc_0041073C: lea edx, var_A0
  loc_00410742: push edx
  loc_00410743: mov eax, Me
  loc_00410746: mov ecx, [eax]
  loc_00410748: mov edx, Me
  loc_0041074B: push edx
  loc_0041074C: call [ecx+00000708h]
  loc_00410752: mov var_2C0, eax
  loc_00410758: cmp var_2C0, 00000000h
  loc_0041075F: jge 00410784h
  loc_00410761: push 00000708h
  loc_00410766: push 0040579Ch ; "#]=VｫoyAｷ ;ﾑs：ﾚLabel12"
  loc_0041076B: mov eax, Me
  loc_0041076E: push eax
  loc_0041076F: mov ecx, var_2C0
  loc_00410775: push ecx
  loc_00410776: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041077C: mov var_4B0, eax
  loc_00410782: jmp 0041078Eh
  loc_00410784: mov var_4B0, 00000000h
  loc_0041078E: lea ecx, var_138
  loc_00410794: call [00401020h] ; __vbaFreeVar
  loc_0041079A: mov var_160, 80020004h
  loc_004107A4: mov var_168, 0000000Ah
  loc_004107AE: mov var_150, 80020004h
  loc_004107B8: mov var_158, 0000000Ah
  loc_004107C2: mov var_250, 004050E8h ; "IMT LampElectrical Probing"
  loc_004107CC: mov var_258, 00000008h
  loc_004107D6: lea edx, var_258
  loc_004107DC: lea ecx, var_148
  loc_004107E2: call [004011B4h] ; __vbaVarDup
  loc_004107E8: push 00406BCCh ; "Probe recipe complete!"
  loc_004107ED: push 004054D8h ; vbCrLf
  loc_004107F2: call [00401050h] ; __vbaStrCat
  loc_004107F8: mov edx, eax
  loc_004107FA: lea ecx, var_C8
  loc_00410800: call [004011D0h] ; __vbaStrMove
  loc_00410806: push eax
  loc_00410807: push 00406C00h ; "Click 'OK' to send probe stage home."
  loc_0041080C: call [00401050h] ; __vbaStrCat
  loc_00410812: mov var_130, eax
  loc_00410818: mov var_138, 00000008h
  loc_00410822: lea edx, var_168
  loc_00410828: push edx
  loc_00410829: lea eax, var_158
  loc_0041082F: push eax
  loc_00410830: lea ecx, var_148
  loc_00410836: push ecx
  loc_00410837: push 00000001h
  loc_00410839: lea edx, var_138
  loc_0041083F: push edx
  loc_00410840: call [00401084h] ; rtcMsgBox
  loc_00410846: mov ecx, eax
  loc_00410848: call [004010ECh] ; __vbaI2I4
  loc_0041084E: mov var_18, ax
  loc_00410852: lea ecx, var_C8
  loc_00410858: call [004011F4h] ; __vbaFreeStr
  loc_0041085E: lea eax, var_168
  loc_00410864: push eax
  loc_00410865: lea ecx, var_158
  loc_0041086B: push ecx
  loc_0041086C: lea edx, var_148
  loc_00410872: push edx
  loc_00410873: lea eax, var_138
  loc_00410879: push eax
  loc_0041087A: push 00000004h
  loc_0041087C: call [00401038h] ; __vbaFreeVarList
  loc_00410882: add esp, 00000014h
  loc_00410885: mov ecx, Me
  loc_00410888: mov edx, [ecx]
  loc_0041088A: mov eax, Me
  loc_0041088D: push eax
  loc_0041088E: call [edx+00000390h]
  loc_00410894: push eax
  loc_00410895: lea ecx, var_118
  loc_0041089B: push ecx
  loc_0041089C: call [00401080h] ; __vbaObjSet
  loc_004108A2: mov var_2C0, eax
  loc_004108A8: push 00406C50h ; "GO"
  loc_004108AD: mov edx, var_2C0
  loc_004108B3: mov eax, [edx]
  loc_004108B5: mov ecx, var_2C0
  loc_004108BB: push ecx
  loc_004108BC: call [eax+00000054h]
  loc_004108BF: fnclex
  loc_004108C1: mov var_2C4, eax
  loc_004108C7: cmp var_2C4, 00000000h
  loc_004108CE: jge 004108F3h
  loc_004108D0: push 00000054h
  loc_004108D2: push 00406128h
  loc_004108D7: mov edx, var_2C0
  loc_004108DD: push edx
  loc_004108DE: mov eax, var_2C4
  loc_004108E4: push eax
  loc_004108E5: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004108EB: mov var_4B4, eax
  loc_004108F1: jmp 004108FDh
  loc_004108F3: mov var_4B4, 00000000h
  loc_004108FD: lea ecx, var_118
  loc_00410903: call [004011F0h] ; __vbaFreeObj
  loc_00410909: movsx ecx, var_18
  loc_0041090D: cmp ecx, 00000001h
  loc_00410910: jnz 004109A4h
  loc_00410916: mov var_130, FFFFFFFFh
  loc_00410920: mov var_138, 0000000Bh
  loc_0041092A: mov edx, 00406C5Ch ; "HO"
  loc_0041092F: lea ecx, var_CC
  loc_00410935: call [00401178h] ; __vbaStrCopy
  loc_0041093B: mov edx, 00406454h ; "2001X"
  loc_00410940: lea ecx, var_C8
  loc_00410946: call [00401178h] ; __vbaStrCopy
  loc_0041094C: lea edx, var_138
  loc_00410952: push edx
  loc_00410953: lea eax, var_CC
  loc_00410959: push eax
  loc_0041095A: lea ecx, var_C8
  loc_00410960: push ecx
  loc_00410961: lea edx, var_148
  loc_00410967: push edx
  loc_00410968: call 0041CA40h
  loc_0041096D: lea edx, var_148
  loc_00410973: lea ecx, var_84
  loc_00410979: call [00401014h] ; __vbaVarMove
  loc_0041097F: lea eax, var_CC
  loc_00410985: push eax
  loc_00410986: lea ecx, var_C8
  loc_0041098C: push ecx
  loc_0041098D: push 00000002h
  loc_0041098F: call [00401180h] ; __vbaFreeStrList
  loc_00410995: add esp, 0000000Ch
  loc_00410998: lea ecx, var_138
  loc_0041099E: call [00401020h] ; __vbaFreeVar
  loc_004109A4: jmp 00413027h
  loc_004109A9: mov edx, Me
  loc_004109AC: mov eax, [edx]
  loc_004109AE: mov ecx, Me
  loc_004109B1: push ecx
  loc_004109B2: call [eax+00000368h]
  loc_004109B8: push eax
  loc_004109B9: lea edx, var_118
  loc_004109BF: push edx
  loc_004109C0: call [00401080h] ; __vbaObjSet
  loc_004109C6: mov var_2C0, eax
  loc_004109CC: lea eax, var_28C
  loc_004109D2: push eax
  loc_004109D3: mov ecx, var_2C0
  loc_004109D9: mov edx, [ecx]
  loc_004109DB: mov eax, var_2C0
  loc_004109E1: push eax
  loc_004109E2: call [edx+000000E0h]
  loc_004109E8: fnclex
  loc_004109EA: mov var_2C4, eax
  loc_004109F0: cmp var_2C4, 00000000h
  loc_004109F7: jge 00410A1Fh
  loc_004109F9: push 000000E0h
  loc_004109FE: push 00405354h
  loc_00410A03: mov ecx, var_2C0
  loc_00410A09: push ecx
  loc_00410A0A: mov edx, var_2C4
  loc_00410A10: push edx
  loc_00410A11: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00410A17: mov var_4B8, eax
  loc_00410A1D: jmp 00410A29h
  loc_00410A1F: mov var_4B8, 00000000h
  loc_00410A29: movsx eax, var_28C
  loc_00410A30: sub eax, 00000001h
  loc_00410A33: neg eax
  loc_00410A35: sbb eax, eax
  loc_00410A37: inc eax
  loc_00410A38: neg eax
  loc_00410A3A: mov var_2C8, ax
  loc_00410A41: lea ecx, var_118
  loc_00410A47: call [004011F0h] ; __vbaFreeObj
  loc_00410A4D: movsx ecx, var_2C8
  loc_00410A54: test ecx, ecx
  loc_00410A56: jz 004110BFh
  loc_00410A5C: push 00423024h
  loc_00410A61: call 0041DD00h
  loc_00410A66: mov var_A0, eax
  loc_00410A6C: mov edx, Me
  loc_00410A6F: mov eax, [edx]
  loc_00410A71: mov ecx, Me
  loc_00410A74: push ecx
  loc_00410A75: call [eax+00000364h]
  loc_00410A7B: push eax
  loc_00410A7C: lea edx, var_118
  loc_00410A82: push edx
  loc_00410A83: call [00401080h] ; __vbaObjSet
  loc_00410A89: mov var_2C0, eax
  loc_00410A8F: lea eax, var_C8
  loc_00410A95: push eax
  loc_00410A96: mov ecx, var_2C0
  loc_00410A9C: mov edx, [ecx]
  loc_00410A9E: mov eax, var_2C0
  loc_00410AA4: push eax
  loc_00410AA5: call [edx+000000A0h]
  loc_00410AAB: fnclex
  loc_00410AAD: mov var_2C4, eax
  loc_00410AB3: cmp var_2C4, 00000000h
  loc_00410ABA: jge 00410AE2h
  loc_00410ABC: push 000000A0h
  loc_00410AC1: push 00405398h
  loc_00410AC6: mov ecx, var_2C0
  loc_00410ACC: push ecx
  loc_00410ACD: mov edx, var_2C4
  loc_00410AD3: push edx
  loc_00410AD4: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00410ADA: mov var_4BC, eax
  loc_00410AE0: jmp 00410AECh
  loc_00410AE2: mov var_4BC, 00000000h
  loc_00410AEC: mov eax, Me
  loc_00410AEF: mov ecx, [eax]
  loc_00410AF1: mov edx, Me
  loc_00410AF4: push edx
  loc_00410AF5: call [ecx+00000324h]
  loc_00410AFB: push eax
  loc_00410AFC: lea eax, var_11C
  loc_00410B02: push eax
  loc_00410B03: call [00401080h] ; __vbaObjSet
  loc_00410B09: mov var_2C8, eax
  loc_00410B0F: lea ecx, var_F4
  loc_00410B15: push ecx
  loc_00410B16: mov edx, var_2C8
  loc_00410B1C: mov eax, [edx]
  loc_00410B1E: mov ecx, var_2C8
  loc_00410B24: push ecx
  loc_00410B25: call [eax+000000A8h]
  loc_00410B2B: fnclex
  loc_00410B2D: mov var_2CC, eax
  loc_00410B33: cmp var_2CC, 00000000h
  loc_00410B3A: jge 00410B62h
  loc_00410B3C: push 000000A8h
  loc_00410B41: push 004055DCh
  loc_00410B46: mov edx, var_2C8
  loc_00410B4C: push edx
  loc_00410B4D: mov eax, var_2CC
  loc_00410B53: push eax
  loc_00410B54: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00410B5A: mov var_4C0, eax
  loc_00410B60: jmp 00410B6Ch
  loc_00410B62: mov var_4C0, 00000000h
  loc_00410B6C: mov ecx, Me
  loc_00410B6F: mov edx, [ecx]
  loc_00410B71: mov eax, Me
  loc_00410B74: push eax
  loc_00410B75: call [edx+00000320h]
  loc_00410B7B: push eax
  loc_00410B7C: lea ecx, var_120
  loc_00410B82: push ecx
  loc_00410B83: call [00401080h] ; __vbaObjSet
  loc_00410B89: mov var_2D0, eax
  loc_00410B8F: lea edx, var_F8
  loc_00410B95: push edx
  loc_00410B96: mov eax, var_2D0
  loc_00410B9C: mov ecx, [eax]
  loc_00410B9E: mov edx, var_2D0
  loc_00410BA4: push edx
  loc_00410BA5: call [ecx+000000A0h]
  loc_00410BAB: fnclex
  loc_00410BAD: mov var_2D4, eax
  loc_00410BB3: cmp var_2D4, 00000000h
  loc_00410BBA: jge 00410BE2h
  loc_00410BBC: push 000000A0h
  loc_00410BC1: push 00405398h
  loc_00410BC6: mov eax, var_2D0
  loc_00410BCC: push eax
  loc_00410BCD: mov ecx, var_2D4
  loc_00410BD3: push ecx
  loc_00410BD4: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00410BDA: mov var_4C4, eax
  loc_00410BE0: jmp 00410BECh
  loc_00410BE2: mov var_4C4, 00000000h
  loc_00410BEC: mov edx, Me
  loc_00410BEF: mov eax, [edx]
  loc_00410BF1: mov ecx, Me
  loc_00410BF4: push ecx
  loc_00410BF5: call [eax+0000031Ch]
  loc_00410BFB: push eax
  loc_00410BFC: lea edx, var_124
  loc_00410C02: push edx
  loc_00410C03: call [00401080h] ; __vbaObjSet
  loc_00410C09: mov var_2D8, eax
  loc_00410C0F: lea eax, var_FC
  loc_00410C15: push eax
  loc_00410C16: mov ecx, var_2D8
  loc_00410C1C: mov edx, [ecx]
  loc_00410C1E: mov eax, var_2D8
  loc_00410C24: push eax
  loc_00410C25: call [edx+000000A0h]
  loc_00410C2B: fnclex
  loc_00410C2D: mov var_2DC, eax
  loc_00410C33: cmp var_2DC, 00000000h
  loc_00410C3A: jge 00410C62h
  loc_00410C3C: push 000000A0h
  loc_00410C41: push 00405398h
  loc_00410C46: mov ecx, var_2D8
  loc_00410C4C: push ecx
  loc_00410C4D: mov edx, var_2DC
  loc_00410C53: push edx
  loc_00410C54: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00410C5A: mov var_4C8, eax
  loc_00410C60: jmp 00410C6Ch
  loc_00410C62: mov var_4C8, 00000000h
  loc_00410C6C: mov eax, Me
  loc_00410C6F: mov ecx, [eax]
  loc_00410C71: mov edx, Me
  loc_00410C74: push edx
  loc_00410C75: call [ecx+00000318h]
  loc_00410C7B: push eax
  loc_00410C7C: lea eax, var_128
  loc_00410C82: push eax
  loc_00410C83: call [00401080h] ; __vbaObjSet
  loc_00410C89: mov var_2E0, eax
  loc_00410C8F: lea ecx, var_100
  loc_00410C95: push ecx
  loc_00410C96: mov edx, var_2E0
  loc_00410C9C: mov eax, [edx]
  loc_00410C9E: mov ecx, var_2E0
  loc_00410CA4: push ecx
  loc_00410CA5: call [eax+000000A0h]
  loc_00410CAB: fnclex
  loc_00410CAD: mov var_2E4, eax
  loc_00410CB3: cmp var_2E4, 00000000h
  loc_00410CBA: jge 00410CE2h
  loc_00410CBC: push 000000A0h
  loc_00410CC1: push 00405398h
  loc_00410CC6: mov edx, var_2E0
  loc_00410CCC: push edx
  loc_00410CCD: mov eax, var_2E4
  loc_00410CD3: push eax
  loc_00410CD4: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00410CDA: mov var_4CC, eax
  loc_00410CE0: jmp 00410CECh
  loc_00410CE2: mov var_4CC, 00000000h
  loc_00410CEC: mov edx, 00406910h ; "Averages"
  loc_00410CF1: lea ecx, var_CC
  loc_00410CF7: call [00401178h] ; __vbaStrCopy
  loc_00410CFD: lea ecx, var_D0
  loc_00410D03: push ecx
  loc_00410D04: lea edx, var_CC
  loc_00410D0A: push edx
  loc_00410D0B: mov eax, var_C0
  loc_00410D11: mov ecx, [eax]
  loc_00410D13: mov edx, var_C0
  loc_00410D19: push edx
  loc_00410D1A: call [ecx+0000002Ch]
  loc_00410D1D: fnclex
  loc_00410D1F: mov var_2E8, eax
  loc_00410D25: cmp var_2E8, 00000000h
  loc_00410D2C: jge 00410D51h
  loc_00410D2E: push 0000002Ch
  loc_00410D30: push 00405B8Ch
  loc_00410D35: mov eax, var_C0
  loc_00410D3B: push eax
  loc_00410D3C: mov ecx, var_2E8
  loc_00410D42: push ecx
  loc_00410D43: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00410D49: mov var_4D0, eax
  loc_00410D4F: jmp 00410D5Bh
  loc_00410D51: mov var_4D0, 00000000h
  loc_00410D5B: mov edx, 004068A8h ; "MeterDelay"
  loc_00410D60: lea ecx, var_D4
  loc_00410D66: call [00401178h] ; __vbaStrCopy
  loc_00410D6C: lea edx, var_D8
  loc_00410D72: push edx
  loc_00410D73: lea eax, var_D4
  loc_00410D79: push eax
  loc_00410D7A: mov ecx, var_C0
  loc_00410D80: mov edx, [ecx]
  loc_00410D82: mov eax, var_C0
  loc_00410D88: push eax
  loc_00410D89: call [edx+0000002Ch]
  loc_00410D8C: fnclex
  loc_00410D8E: mov var_2EC, eax
  loc_00410D94: cmp var_2EC, 00000000h
  loc_00410D9B: jge 00410DC0h
  loc_00410D9D: push 0000002Ch
  loc_00410D9F: push 00405B8Ch
  loc_00410DA4: mov ecx, var_C0
  loc_00410DAA: push ecx
  loc_00410DAB: mov edx, var_2EC
  loc_00410DB1: push edx
  loc_00410DB2: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00410DB8: mov var_4D4, eax
  loc_00410DBE: jmp 00410DCAh
  loc_00410DC0: mov var_4D4, 00000000h
  loc_00410DCA: mov edx, 00406844h ; "Iterations"
  loc_00410DCF: lea ecx, var_DC
  loc_00410DD5: call [00401178h] ; __vbaStrCopy
  loc_00410DDB: lea eax, var_E0
  loc_00410DE1: push eax
  loc_00410DE2: lea ecx, var_DC
  loc_00410DE8: push ecx
  loc_00410DE9: mov edx, var_C0
  loc_00410DEF: mov eax, [edx]
  loc_00410DF1: mov ecx, var_C0
  loc_00410DF7: push ecx
  loc_00410DF8: call [eax+0000002Ch]
  loc_00410DFB: fnclex
  loc_00410DFD: mov var_2F0, eax
  loc_00410E03: cmp var_2F0, 00000000h
  loc_00410E0A: jge 00410E2Fh
  loc_00410E0C: push 0000002Ch
  loc_00410E0E: push 00405B8Ch
  loc_00410E13: mov edx, var_C0
  loc_00410E19: push edx
  loc_00410E1A: mov eax, var_2F0
  loc_00410E20: push eax
  loc_00410E21: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00410E27: mov var_4D8, eax
  loc_00410E2D: jmp 00410E39h
  loc_00410E2F: mov var_4D8, 00000000h
  loc_00410E39: mov edx, 004069F8h ; "NPLC"
  loc_00410E3E: lea ecx, var_E4
  loc_00410E44: call [00401178h] ; __vbaStrCopy
  loc_00410E4A: lea ecx, var_E8
  loc_00410E50: push ecx
  loc_00410E51: lea edx, var_E4
  loc_00410E57: push edx
  loc_00410E58: mov eax, var_C0
  loc_00410E5E: mov ecx, [eax]
  loc_00410E60: mov edx, var_C0
  loc_00410E66: push edx
  loc_00410E67: call [ecx+0000002Ch]
  loc_00410E6A: fnclex
  loc_00410E6C: mov var_2F4, eax
  loc_00410E72: cmp var_2F4, 00000000h
  loc_00410E79: jge 00410E9Eh
  loc_00410E7B: push 0000002Ch
  loc_00410E7D: push 00405B8Ch
  loc_00410E82: mov eax, var_C0
  loc_00410E88: push eax
  loc_00410E89: mov ecx, var_2F4
  loc_00410E8F: push ecx
  loc_00410E90: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00410E96: mov var_4DC, eax
  loc_00410E9C: jmp 00410EA8h
  loc_00410E9E: mov var_4DC, 00000000h
  loc_00410EA8: mov edx, var_E8
  loc_00410EAE: push edx
  loc_00410EAF: call [0040117Ch] ; __vbaI4Str
  loc_00410EB5: mov var_2A4, eax
  loc_00410EBB: mov eax, var_E0
  loc_00410EC1: push eax
  loc_00410EC2: call [0040117Ch] ; __vbaI4Str
  loc_00410EC8: mov var_2A0, eax
  loc_00410ECE: mov ecx, var_D8
  loc_00410ED4: push ecx
  loc_00410ED5: call [00401160h] ; __vbaR8Str
  loc_00410EDB: fstp real8 ptr var_2B4
  loc_00410EE1: mov edx, var_D0
  loc_00410EE7: push edx
  loc_00410EE8: call [0040117Ch] ; __vbaI4Str
  loc_00410EEE: mov var_29C, eax
  loc_00410EF4: mov eax, var_100
  loc_00410EFA: push eax
  loc_00410EFB: call [0040117Ch] ; __vbaI4Str
  loc_00410F01: mov var_298, eax
  loc_00410F07: mov ecx, var_FC
  loc_00410F0D: push ecx
  loc_00410F0E: call [0040117Ch] ; __vbaI4Str
  loc_00410F14: mov var_294, eax
  loc_00410F1A: mov edx, var_F8
  loc_00410F20: push edx
  loc_00410F21: call [0040117Ch] ; __vbaI4Str
  loc_00410F27: mov var_290, eax
  loc_00410F2D: mov eax, var_F4
  loc_00410F33: push eax
  loc_00410F34: call [00401160h] ; __vbaR8Str
  loc_00410F3A: fstp real8 ptr var_2AC
  loc_00410F40: mov edx, 00406C68h ; "Engineering Mode"
  loc_00410F45: lea ecx, var_F0
  loc_00410F4B: call [00401178h] ; __vbaStrCopy
  loc_00410F51: mov ecx, var_C8
  loc_00410F57: mov var_34C, ecx
  loc_00410F5D: mov var_C8, 00000000h
  loc_00410F67: mov edx, var_34C
  loc_00410F6D: lea ecx, var_EC
  loc_00410F73: call [004011D0h] ; __vbaStrMove
  loc_00410F79: lea edx, var_138
  loc_00410F7F: push edx
  loc_00410F80: lea eax, var_2A4
  loc_00410F86: push eax
  loc_00410F87: lea ecx, var_2A0
  loc_00410F8D: push ecx
  loc_00410F8E: lea edx, var_2B4
  loc_00410F94: push edx
  loc_00410F95: lea eax, var_29C
  loc_00410F9B: push eax
  loc_00410F9C: lea ecx, var_298
  loc_00410FA2: push ecx
  loc_00410FA3: lea edx, var_294
  loc_00410FA9: push edx
  loc_00410FAA: lea eax, var_290
  loc_00410FB0: push eax
  loc_00410FB1: lea ecx, var_2AC
  loc_00410FB7: push ecx
  loc_00410FB8: lea edx, var_F0
  loc_00410FBE: push edx
  loc_00410FBF: lea eax, var_EC
  loc_00410FC5: push eax
  loc_00410FC6: lea ecx, var_A0
  loc_00410FCC: push ecx
  loc_00410FCD: mov edx, Me
  loc_00410FD0: mov eax, [edx]
  loc_00410FD2: mov ecx, Me
  loc_00410FD5: push ecx
  loc_00410FD6: call [eax+000006FCh]
  loc_00410FDC: mov var_2F8, eax
  loc_00410FE2: cmp var_2F8, 00000000h
  loc_00410FE9: jge 0041100Eh
  loc_00410FEB: push 000006FCh
  loc_00410FF0: push 0040579Ch ; "#]=VｫoyAｷ ;ﾑs：ﾚLabel12"
  loc_00410FF5: mov edx, Me
  loc_00410FF8: push edx
  loc_00410FF9: mov eax, var_2F8
  loc_00410FFF: push eax
  loc_00411000: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00411006: mov var_4E0, eax
  loc_0041100C: jmp 00411018h
  loc_0041100E: mov var_4E0, 00000000h
  loc_00411018: lea ecx, var_E8
  loc_0041101E: push ecx
  loc_0041101F: lea edx, var_E0
  loc_00411025: push edx
  loc_00411026: lea eax, var_D8
  loc_0041102C: push eax
  loc_0041102D: lea ecx, var_D0
  loc_00411033: push ecx
  loc_00411034: lea edx, var_100
  loc_0041103A: push edx
  loc_0041103B: lea eax, var_FC
  loc_00411041: push eax
  loc_00411042: lea ecx, var_F8
  loc_00411048: push ecx
  loc_00411049: lea edx, var_F4
  loc_0041104F: push edx
  loc_00411050: lea eax, var_F0
  loc_00411056: push eax
  loc_00411057: lea ecx, var_EC
  loc_0041105D: push ecx
  loc_0041105E: lea edx, var_E4
  loc_00411064: push edx
  loc_00411065: lea eax, var_DC
  loc_0041106B: push eax
  loc_0041106C: lea ecx, var_D4
  loc_00411072: push ecx
  loc_00411073: lea edx, var_CC
  loc_00411079: push edx
  loc_0041107A: push 0000000Eh
  loc_0041107C: call [00401180h] ; __vbaFreeStrList
  loc_00411082: add esp, 0000003Ch
  loc_00411085: lea eax, var_128
  loc_0041108B: push eax
  loc_0041108C: lea ecx, var_124
  loc_00411092: push ecx
  loc_00411093: lea edx, var_120
  loc_00411099: push edx
  loc_0041109A: lea eax, var_11C
  loc_004110A0: push eax
  loc_004110A1: lea ecx, var_118
  loc_004110A7: push ecx
  loc_004110A8: push 00000005h
  loc_004110AA: call [00401040h] ; __vbaFreeObjList
  loc_004110B0: add esp, 00000018h
  loc_004110B3: lea ecx, var_138
  loc_004110B9: call [00401020h] ; __vbaFreeVar
  loc_004110BF: mov edx, Me
  loc_004110C2: mov eax, [edx]
  loc_004110C4: mov ecx, Me
  loc_004110C7: push ecx
  loc_004110C8: call [eax+00000378h]
  loc_004110CE: push eax
  loc_004110CF: lea edx, var_118
  loc_004110D5: push edx
  loc_004110D6: call [00401080h] ; __vbaObjSet
  loc_004110DC: mov var_2C0, eax
  loc_004110E2: lea eax, var_28C
  loc_004110E8: push eax
  loc_004110E9: mov ecx, var_2C0
  loc_004110EF: mov edx, [ecx]
  loc_004110F1: mov eax, var_2C0
  loc_004110F7: push eax
  loc_004110F8: call [edx+000000E0h]
  loc_004110FE: fnclex
  loc_00411100: mov var_2C4, eax
  loc_00411106: cmp var_2C4, 00000000h
  loc_0041110D: jge 00411135h
  loc_0041110F: push 000000E0h
  loc_00411114: push 00405388h
  loc_00411119: mov ecx, var_2C0
  loc_0041111F: push ecx
  loc_00411120: mov edx, var_2C4
  loc_00411126: push edx
  loc_00411127: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041112D: mov var_4E4, eax
  loc_00411133: jmp 0041113Fh
  loc_00411135: mov var_4E4, 00000000h
  loc_0041113F: xor eax, eax
  loc_00411141: cmp var_28C, FFFFFFh
  loc_00411149: setz al
  loc_0041114C: neg eax
  loc_0041114E: mov var_2C8, ax
  loc_00411155: lea ecx, var_118
  loc_0041115B: call [004011F0h] ; __vbaFreeObj
  loc_00411161: movsx ecx, var_2C8
  loc_00411168: test ecx, ecx
  loc_0041116A: jz 004126BAh
  loc_00411170: mov edx, Me
  loc_00411173: cmp [edx+0000004Ch], 00000000h
  loc_00411177: jz 0041125Dh
  loc_0041117D: mov eax, Me
  loc_00411180: mov ecx, [eax+0000004Ch]
  loc_00411183: cmp [ecx], 0001h
  loc_00411187: jnz 0041125Dh
  loc_0041118D: mov edx, Me
  loc_00411190: mov eax, [edx]
  loc_00411192: mov ecx, Me
  loc_00411195: push ecx
  loc_00411196: call [eax+00000370h]
  loc_0041119C: push eax
  loc_0041119D: lea edx, var_118
  loc_004111A3: push edx
  loc_004111A4: call [00401080h] ; __vbaObjSet
  loc_004111AA: mov var_2C0, eax
  loc_004111B0: lea eax, var_28C
  loc_004111B6: push eax
  loc_004111B7: mov ecx, var_2C0
  loc_004111BD: mov edx, [ecx]
  loc_004111BF: mov eax, var_2C0
  loc_004111C5: push eax
  loc_004111C6: call [edx+000000F0h]
  loc_004111CC: fnclex
  loc_004111CE: mov var_2C4, eax
  loc_004111D4: cmp var_2C4, 00000000h
  loc_004111DB: jge 00411203h
  loc_004111DD: push 000000F0h
  loc_004111E2: push 004055DCh
  loc_004111E7: mov ecx, var_2C0
  loc_004111ED: push ecx
  loc_004111EE: mov edx, var_2C4
  loc_004111F4: push edx
  loc_004111F5: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004111FB: mov var_4E8, eax
  loc_00411201: jmp 0041120Dh
  loc_00411203: mov var_4E8, 00000000h
  loc_0041120D: movsx eax, var_28C
  loc_00411214: mov ecx, Me
  loc_00411217: mov edx, [ecx+0000004Ch]
  loc_0041121A: sub eax, [edx+00000014h]
  loc_0041121D: mov var_2C8, eax
  loc_00411223: mov eax, Me
  loc_00411226: mov ecx, [eax+0000004Ch]
  loc_00411229: mov edx, var_2C8
  loc_0041122F: cmp edx, [ecx+00000010h]
  loc_00411232: jae 00411240h
  loc_00411234: mov var_4EC, 00000000h
  loc_0041123E: jmp 0041124Ch
  loc_00411240: call [004010D8h] ; __vbaGenerateBoundsError
  loc_00411246: mov var_4EC, eax
  loc_0041124C: mov eax, var_2C8
  loc_00411252: shl eax, 02h
  loc_00411255: mov var_4F0, eax
  loc_0041125B: jmp 00411269h
  loc_0041125D: call [004010D8h] ; __vbaGenerateBoundsError
  loc_00411263: mov var_4F0, eax
  loc_00411269: mov ecx, Me
  loc_0041126C: mov edx, [ecx+0000004Ch]
  loc_0041126F: mov eax, [edx+0000000Ch]
  loc_00411272: mov ecx, var_4F0
  loc_00411278: mov edx, [eax+ecx]
  loc_0041127B: lea ecx, var_40
  loc_0041127E: call [00401178h] ; __vbaStrCopy
  loc_00411284: lea ecx, var_118
  loc_0041128A: call [004011F0h] ; __vbaFreeObj
  loc_00411290: mov edx, Me
  loc_00411293: mov eax, [edx]
  loc_00411295: mov ecx, Me
  loc_00411298: push ecx
  loc_00411299: call [eax+00000370h]
  loc_0041129F: push eax
  loc_004112A0: lea edx, var_118
  loc_004112A6: push edx
  loc_004112A7: call [00401080h] ; __vbaObjSet
  loc_004112AD: mov var_2C0, eax
  loc_004112B3: lea eax, var_28C
  loc_004112B9: push eax
  loc_004112BA: mov ecx, var_2C0
  loc_004112C0: mov edx, [ecx]
  loc_004112C2: mov eax, var_2C0
  loc_004112C8: push eax
  loc_004112C9: call [edx+000000F0h]
  loc_004112CF: fnclex
  loc_004112D1: mov var_2C4, eax
  loc_004112D7: cmp var_2C4, 00000000h
  loc_004112DE: jge 00411306h
  loc_004112E0: push 000000F0h
  loc_004112E5: push 004055DCh
  loc_004112EA: mov ecx, var_2C0
  loc_004112F0: push ecx
  loc_004112F1: mov edx, var_2C4
  loc_004112F7: push edx
  loc_004112F8: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004112FE: mov var_4F4, eax
  loc_00411304: jmp 00411310h
  loc_00411306: mov var_4F4, 00000000h
  loc_00411310: mov var_160, 80020004h
  loc_0041131A: mov var_168, 0000000Ah
  loc_00411324: mov var_150, 80020004h
  loc_0041132E: mov var_158, 0000000Ah
  loc_00411338: mov var_250, 004050E8h ; "IMT LampElectrical Probing"
  loc_00411342: mov var_258, 00000008h
  loc_0041134C: lea edx, var_258
  loc_00411352: lea ecx, var_148
  loc_00411358: call [004011B4h] ; __vbaVarDup
  loc_0041135E: mov eax, Me
  loc_00411361: cmp [eax+0000004Ch], 00000000h
  loc_00411365: jz 004113C3h
  loc_00411367: mov ecx, Me
  loc_0041136A: mov edx, [ecx+0000004Ch]
  loc_0041136D: cmp [edx], 0001h
  loc_00411371: jnz 004113C3h
  loc_00411373: movsx eax, var_28C
  loc_0041137A: mov ecx, Me
  loc_0041137D: mov edx, [ecx+0000004Ch]
  loc_00411380: sub eax, [edx+00000014h]
  loc_00411383: mov var_2C8, eax
  loc_00411389: mov eax, Me
  loc_0041138C: mov ecx, [eax+0000004Ch]
  loc_0041138F: mov edx, var_2C8
  loc_00411395: cmp edx, [ecx+00000010h]
  loc_00411398: jae 004113A6h
  loc_0041139A: mov var_4F8, 00000000h
  loc_004113A4: jmp 004113B2h
  loc_004113A6: call [004010D8h] ; __vbaGenerateBoundsError
  loc_004113AC: mov var_4F8, eax
  loc_004113B2: mov eax, var_2C8
  loc_004113B8: shl eax, 02h
  loc_004113BB: mov var_4FC, eax
  loc_004113C1: jmp 004113CFh
  loc_004113C3: call [004010D8h] ; __vbaGenerateBoundsError
  loc_004113C9: mov var_4FC, eax
  loc_004113CF: push 00406C90h ; "Click OK to make the move from the align site to "
  loc_004113D4: mov ecx, Me
  loc_004113D7: mov edx, [ecx+0000004Ch]
  loc_004113DA: mov eax, [edx+0000000Ch]
  loc_004113DD: mov ecx, var_4FC
  loc_004113E3: mov edx, [eax+ecx]
  loc_004113E6: push edx
  loc_004113E7: call [00401050h] ; __vbaStrCat
  loc_004113ED: mov var_130, eax
  loc_004113F3: mov var_138, 00000008h
  loc_004113FD: lea eax, var_168
  loc_00411403: push eax
  loc_00411404: lea ecx, var_158
  loc_0041140A: push ecx
  loc_0041140B: lea edx, var_148
  loc_00411411: push edx
  loc_00411412: push 00000001h
  loc_00411414: lea eax, var_138
  loc_0041141A: push eax
  loc_0041141B: call [00401084h] ; rtcMsgBox
  loc_00411421: mov ecx, eax
  loc_00411423: call [004010ECh] ; __vbaI2I4
  loc_00411429: mov var_18, ax
  loc_0041142D: lea ecx, var_118
  loc_00411433: call [004011F0h] ; __vbaFreeObj
  loc_00411439: lea ecx, var_168
  loc_0041143F: push ecx
  loc_00411440: lea edx, var_158
  loc_00411446: push edx
  loc_00411447: lea eax, var_148
  loc_0041144D: push eax
  loc_0041144E: lea ecx, var_138
  loc_00411454: push ecx
  loc_00411455: push 00000004h
  loc_00411457: call [00401038h] ; __vbaFreeVarList
  loc_0041145D: add esp, 00000014h
  loc_00411460: movsx edx, var_18
  loc_00411464: cmp edx, 00000002h
  loc_00411467: jnz 0041146Eh
  loc_00411469: jmp 0041489Fh
  loc_0041146E: mov edx, 0040639Ch ; "XMoveFirstFromAlignSite"
  loc_00411473: lea ecx, var_C8
  loc_00411479: call [00401178h] ; __vbaStrCopy
  loc_0041147F: lea eax, var_CC
  loc_00411485: push eax
  loc_00411486: lea ecx, var_C8
  loc_0041148C: push ecx
  loc_0041148D: mov edx, var_C0
  loc_00411493: mov eax, [edx]
  loc_00411495: mov ecx, var_C0
  loc_0041149B: push ecx
  loc_0041149C: call [eax+0000002Ch]
  loc_0041149F: fnclex
  loc_004114A1: mov var_2C0, eax
  loc_004114A7: cmp var_2C0, 00000000h
  loc_004114AE: jge 004114D3h
  loc_004114B0: push 0000002Ch
  loc_004114B2: push 00405B8Ch
  loc_004114B7: mov edx, var_C0
  loc_004114BD: push edx
  loc_004114BE: mov eax, var_2C0
  loc_004114C4: push eax
  loc_004114C5: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004114CB: mov var_500, eax
  loc_004114D1: jmp 004114DDh
  loc_004114D3: mov var_500, 00000000h
  loc_004114DD: mov ecx, var_CC
  loc_004114E3: mov var_350, ecx
  loc_004114E9: mov var_CC, 00000000h
  loc_004114F3: mov edx, var_350
  loc_004114F9: mov var_130, edx
  loc_004114FF: mov var_138, 00000008h
  loc_00411509: lea eax, var_138
  loc_0041150F: push eax
  loc_00411510: call 0041DBB0h
  loc_00411515: fstp real8 ptr var_54
  loc_00411518: lea ecx, var_C8
  loc_0041151E: call [004011F4h] ; __vbaFreeStr
  loc_00411524: lea ecx, var_138
  loc_0041152A: call [00401020h] ; __vbaFreeVar
  loc_00411530: mov edx, 004063DCh ; "YMoveFirstFromAlignSite"
  loc_00411535: lea ecx, var_C8
  loc_0041153B: call [00401178h] ; __vbaStrCopy
  loc_00411541: lea ecx, var_CC
  loc_00411547: push ecx
  loc_00411548: lea edx, var_C8
  loc_0041154E: push edx
  loc_0041154F: mov eax, var_C0
  loc_00411555: mov ecx, [eax]
  loc_00411557: mov edx, var_C0
  loc_0041155D: push edx
  loc_0041155E: call [ecx+0000002Ch]
  loc_00411561: fnclex
  loc_00411563: mov var_2C0, eax
  loc_00411569: cmp var_2C0, 00000000h
  loc_00411570: jge 00411595h
  loc_00411572: push 0000002Ch
  loc_00411574: push 00405B8Ch
  loc_00411579: mov eax, var_C0
  loc_0041157F: push eax
  loc_00411580: mov ecx, var_2C0
  loc_00411586: push ecx
  loc_00411587: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041158D: mov var_504, eax
  loc_00411593: jmp 0041159Fh
  loc_00411595: mov var_504, 00000000h
  loc_0041159F: mov edx, var_CC
  loc_004115A5: mov var_354, edx
  loc_004115AB: mov var_CC, 00000000h
  loc_004115B5: mov eax, var_354
  loc_004115BB: mov var_130, eax
  loc_004115C1: mov var_138, 00000008h
  loc_004115CB: lea ecx, var_138
  loc_004115D1: push ecx
  loc_004115D2: call 0041DBB0h
  loc_004115D7: fstp real8 ptr var_90
  loc_004115DD: lea ecx, var_C8
  loc_004115E3: call [004011F4h] ; __vbaFreeStr
  loc_004115E9: lea ecx, var_138
  loc_004115EF: call [00401020h] ; __vbaFreeVar
  loc_004115F5: fld real8 ptr var_54
  loc_004115F8: fcomp real8 ptr [00401288h]
  loc_004115FE: fnstsw ax
  loc_00411600: test ah, 40h
  loc_00411603: jz 00411611h
  loc_00411605: mov var_508, 00000001h
  loc_0041160F: jmp 0041161Bh
  loc_00411611: mov var_508, 00000000h
  loc_0041161B: fld real8 ptr var_90
  loc_00411621: fcomp real8 ptr [00401288h]
  loc_00411627: fnstsw ax
  loc_00411629: test ah, 40h
  loc_0041162C: jz 0041163Ah
  loc_0041162E: mov var_50C, 00000001h
  loc_00411638: jmp 00411644h
  loc_0041163A: mov var_50C, 00000000h
  loc_00411644: mov edx, var_508
  loc_0041164A: and edx, var_50C
  loc_00411650: test edx, edx
  loc_00411652: jnz 00411AC3h
  loc_00411658: mov eax, Me
  loc_0041165B: mov ecx, [eax]
  loc_0041165D: mov edx, Me
  loc_00411660: push edx
  loc_00411661: call [ecx+0000039Ch]
  loc_00411667: push eax
  loc_00411668: lea eax, var_118
  loc_0041166E: push eax
  loc_0041166F: call [00401080h] ; __vbaObjSet
  loc_00411675: mov var_2C0, eax
  loc_0041167B: push 00406410h ; "Moving to first site"
  loc_00411680: mov ecx, var_2C0
  loc_00411686: mov edx, [ecx]
  loc_00411688: mov eax, var_2C0
  loc_0041168E: push eax
  loc_0041168F: call [edx+00000054h]
  loc_00411692: fnclex
  loc_00411694: mov var_2C4, eax
  loc_0041169A: cmp var_2C4, 00000000h
  loc_004116A1: jge 004116C6h
  loc_004116A3: push 00000054h
  loc_004116A5: push 0040575Ch
  loc_004116AA: mov ecx, var_2C0
  loc_004116B0: push ecx
  loc_004116B1: mov edx, var_2C4
  loc_004116B7: push edx
  loc_004116B8: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004116BE: mov var_510, eax
  loc_004116C4: jmp 004116D0h
  loc_004116C6: mov var_510, 00000000h
  loc_004116D0: lea ecx, var_118
  loc_004116D6: call [004011F0h] ; __vbaFreeObj
  loc_004116DC: call [004010A0h] ; rtcDoEvents
  loc_004116E2: mov var_250, 00406440h ; "MMX"
  loc_004116EC: mov var_258, 00000008h
  loc_004116F6: mov eax, var_50
  loc_004116F9: push eax
  loc_004116FA: mov ecx, var_54
  loc_004116FD: push ecx
  loc_004116FE: call [00401104h] ; __vbaStrR8
  loc_00411704: mov var_130, eax
  loc_0041170A: mov var_138, 00000008h
  loc_00411714: lea edx, var_138
  loc_0041171A: push edx
  loc_0041171B: lea eax, var_148
  loc_00411721: push eax
  loc_00411722: call [004010A4h] ; rtcTrimVar
  loc_00411728: mov var_260, 0040644Ch ; "Y"
  loc_00411732: mov var_268, 00000008h
  loc_0041173C: mov ecx, var_8C
  loc_00411742: push ecx
  loc_00411743: mov edx, var_90
  loc_00411749: push edx
  loc_0041174A: call [00401104h] ; __vbaStrR8
  loc_00411750: mov var_170, eax
  loc_00411756: mov var_178, 00000008h
  loc_00411760: lea eax, var_178
  loc_00411766: push eax
  loc_00411767: lea ecx, var_188
  loc_0041176D: push ecx
  loc_0041176E: call [004010A4h] ; rtcTrimVar
  loc_00411774: lea edx, var_258
  loc_0041177A: push edx
  loc_0041177B: lea eax, var_148
  loc_00411781: push eax
  loc_00411782: lea ecx, var_158
  loc_00411788: push ecx
  loc_00411789: call [004011ACh] ; __vbaVarAdd
  loc_0041178F: push eax
  loc_00411790: lea edx, var_268
  loc_00411796: push edx
  loc_00411797: lea eax, var_168
  loc_0041179D: push eax
  loc_0041179E: call [004011ACh] ; __vbaVarAdd
  loc_004117A4: push eax
  loc_004117A5: lea ecx, var_188
  loc_004117AB: push ecx
  loc_004117AC: lea edx, var_198
  loc_004117B2: push edx
  loc_004117B3: call [004011ACh] ; __vbaVarAdd
  loc_004117B9: push eax
  loc_004117BA: call [00401030h] ; __vbaStrVarMove
  loc_004117C0: mov edx, eax
  loc_004117C2: lea ecx, var_58
  loc_004117C5: call [004011D0h] ; __vbaStrMove
  loc_004117CB: lea eax, var_198
  loc_004117D1: push eax
  loc_004117D2: lea ecx, var_188
  loc_004117D8: push ecx
  loc_004117D9: lea edx, var_168
  loc_004117DF: push edx
  loc_004117E0: lea eax, var_178
  loc_004117E6: push eax
  loc_004117E7: lea ecx, var_158
  loc_004117ED: push ecx
  loc_004117EE: lea edx, var_148
  loc_004117F4: push edx
  loc_004117F5: lea eax, var_138
  loc_004117FB: push eax
  loc_004117FC: push 00000007h
  loc_004117FE: call [00401038h] ; __vbaFreeVarList
  loc_00411804: add esp, 00000020h
  loc_00411807: mov var_130, FFFFFFFFh
  loc_00411811: mov var_138, 0000000Bh
  loc_0041181B: mov edx, 00406454h ; "2001X"
  loc_00411820: lea ecx, var_C8
  loc_00411826: call [00401178h] ; __vbaStrCopy
  loc_0041182C: lea ecx, var_138
  loc_00411832: push ecx
  loc_00411833: lea edx, var_58
  loc_00411836: push edx
  loc_00411837: lea eax, var_C8
  loc_0041183D: push eax
  loc_0041183E: lea ecx, var_148
  loc_00411844: push ecx
  loc_00411845: call 0041CA40h
  loc_0041184A: lea edx, var_148
  loc_00411850: lea ecx, var_84
  loc_00411856: call [00401014h] ; __vbaVarMove
  loc_0041185C: lea ecx, var_C8
  loc_00411862: call [004011F4h] ; __vbaFreeStr
  loc_00411868: lea ecx, var_138
  loc_0041186E: call [00401020h] ; __vbaFreeVar
  loc_00411874: lea edx, var_84
  loc_0041187A: push edx
  loc_0041187B: call [00401044h] ; __vbaStrErrVarCopy
  loc_00411881: mov edx, eax
  loc_00411883: lea ecx, var_C8
  loc_00411889: call [004011D0h] ; __vbaStrMove
  loc_0041188F: push eax
  loc_00411890: push 00406464h ; "MC"
  loc_00411895: call [004010DCh] ; __vbaStrCmp
  loc_0041189B: neg eax
  loc_0041189D: sbb eax, eax
  loc_0041189F: neg eax
  loc_004118A1: neg eax
  loc_004118A3: mov var_2C0, ax
  loc_004118AA: lea ecx, var_C8
  loc_004118B0: call [004011F4h] ; __vbaFreeStr
  loc_004118B6: movsx eax, var_2C0
  loc_004118BD: test eax, eax
  loc_004118BF: jz 00411AC3h
  loc_004118C5: mov var_160, 80020004h
  loc_004118CF: mov var_168, 0000000Ah
  loc_004118D9: mov var_150, 80020004h
  loc_004118E3: mov var_158, 0000000Ah
  loc_004118ED: mov var_250, 004050E8h ; "IMT LampElectrical Probing"
  loc_004118F7: mov var_258, 00000008h
  loc_00411901: lea edx, var_258
  loc_00411907: lea ecx, var_148
  loc_0041190D: call [004011B4h] ; __vbaVarDup
  loc_00411913: push 00406470h ; "Prober command '"
  loc_00411918: mov ecx, var_58
  loc_0041191B: push ecx
  loc_0041191C: call [00401050h] ; __vbaStrCat
  loc_00411922: mov edx, eax
  loc_00411924: lea ecx, var_C8
  loc_0041192A: call [004011D0h] ; __vbaStrMove
  loc_00411930: push eax
  loc_00411931: push 00406498h ; "' failed to return 'MC', instead said:"
  loc_00411936: call [00401050h] ; __vbaStrCat
  loc_0041193C: mov edx, eax
  loc_0041193E: lea ecx, var_CC
  loc_00411944: call [004011D0h] ; __vbaStrMove
  loc_0041194A: push eax
  loc_0041194B: push 004054D8h ; vbCrLf
  loc_00411950: call [00401050h] ; __vbaStrCat
  loc_00411956: mov edx, eax
  loc_00411958: lea ecx, var_D0
  loc_0041195E: call [004011D0h] ; __vbaStrMove
  loc_00411964: push eax
  loc_00411965: lea edx, var_84
  loc_0041196B: push edx
  loc_0041196C: call [00401044h] ; __vbaStrErrVarCopy
  loc_00411972: mov edx, eax
  loc_00411974: lea ecx, var_D4
  loc_0041197A: call [004011D0h] ; __vbaStrMove
  loc_00411980: push eax
  loc_00411981: call [00401050h] ; __vbaStrCat
  loc_00411987: mov edx, eax
  loc_00411989: lea ecx, var_D8
  loc_0041198F: call [004011D0h] ; __vbaStrMove
  loc_00411995: push eax
  loc_00411996: push 004054D8h ; vbCrLf
  loc_0041199B: call [00401050h] ; __vbaStrCat
  loc_004119A1: mov edx, eax
  loc_004119A3: lea ecx, var_DC
  loc_004119A9: call [004011D0h] ; __vbaStrMove
  loc_004119AF: push eax
  loc_004119B0: push 004064ECh ; "Continue anyway?"
  loc_004119B5: call [00401050h] ; __vbaStrCat
  loc_004119BB: mov var_130, eax
  loc_004119C1: mov var_138, 00000008h
  loc_004119CB: lea eax, var_168
  loc_004119D1: push eax
  loc_004119D2: lea ecx, var_158
  loc_004119D8: push ecx
  loc_004119D9: lea edx, var_148
  loc_004119DF: push edx
  loc_004119E0: push 00000004h
  loc_004119E2: lea eax, var_138
  loc_004119E8: push eax
  loc_004119E9: call [00401084h] ; rtcMsgBox
  loc_004119EF: mov ecx, eax
  loc_004119F1: call [004010ECh] ; __vbaI2I4
  loc_004119F7: mov var_18, ax
  loc_004119FB: lea ecx, var_DC
  loc_00411A01: push ecx
  loc_00411A02: lea edx, var_D8
  loc_00411A08: push edx
  loc_00411A09: lea eax, var_D4
  loc_00411A0F: push eax
  loc_00411A10: lea ecx, var_D0
  loc_00411A16: push ecx
  loc_00411A17: lea edx, var_CC
  loc_00411A1D: push edx
  loc_00411A1E: lea eax, var_C8
  loc_00411A24: push eax
  loc_00411A25: push 00000006h
  loc_00411A27: call [00401180h] ; __vbaFreeStrList
  loc_00411A2D: add esp, 0000001Ch
  loc_00411A30: lea ecx, var_168
  loc_00411A36: push ecx
  loc_00411A37: lea edx, var_158
  loc_00411A3D: push edx
  loc_00411A3E: lea eax, var_148
  loc_00411A44: push eax
  loc_00411A45: lea ecx, var_138
  loc_00411A4B: push ecx
  loc_00411A4C: push 00000004h
  loc_00411A4E: call [00401038h] ; __vbaFreeVarList
  loc_00411A54: add esp, 00000014h
  loc_00411A57: movsx edx, var_18
  loc_00411A5B: cmp edx, 00000007h
  loc_00411A5E: jnz 00411AC3h
  loc_00411A60: lea eax, var_138
  loc_00411A66: push eax
  loc_00411A67: mov ecx, Me
  loc_00411A6A: mov edx, [ecx]
  loc_00411A6C: mov eax, Me
  loc_00411A6F: push eax
  loc_00411A70: call [edx+00000704h]
  loc_00411A76: mov var_2C0, eax
  loc_00411A7C: cmp var_2C0, 00000000h
  loc_00411A83: jge 00411AA8h
  loc_00411A85: push 00000704h
  loc_00411A8A: push 0040579Ch ; "#]=VｫoyAｷ ;ﾑs：ﾚLabel12"
  loc_00411A8F: mov ecx, Me
  loc_00411A92: push ecx
  loc_00411A93: mov edx, var_2C0
  loc_00411A99: push edx
  loc_00411A9A: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00411AA0: mov var_514, eax
  loc_00411AA6: jmp 00411AB2h
  loc_00411AA8: mov var_514, 00000000h
  loc_00411AB2: lea ecx, var_138
  loc_00411AB8: call [00401020h] ; __vbaFreeVar
  loc_00411ABE: jmp 0041489Fh
  loc_00411AC3: mov var_130, 80020004h
  loc_00411ACD: mov var_138, 0000000Ah
  loc_00411AD7: mov edx, 00406A84h ; "SP2X0Y0"
  loc_00411ADC: lea ecx, var_CC
  loc_00411AE2: call [00401178h] ; __vbaStrCopy
  loc_00411AE8: mov edx, 00406454h ; "2001X"
  loc_00411AED: lea ecx, var_C8
  loc_00411AF3: call [00401178h] ; __vbaStrCopy
  loc_00411AF9: lea eax, var_138
  loc_00411AFF: push eax
  loc_00411B00: lea ecx, var_CC
  loc_00411B06: push ecx
  loc_00411B07: lea edx, var_C8
  loc_00411B0D: push edx
  loc_00411B0E: lea eax, var_148
  loc_00411B14: push eax
  loc_00411B15: call 0041CA40h
  loc_00411B1A: lea edx, var_148
  loc_00411B20: lea ecx, var_84
  loc_00411B26: call [00401014h] ; __vbaVarMove
  loc_00411B2C: lea ecx, var_CC
  loc_00411B32: push ecx
  loc_00411B33: lea edx, var_C8
  loc_00411B39: push edx
  loc_00411B3A: push 00000002h
  loc_00411B3C: call [00401180h] ; __vbaFreeStrList
  loc_00411B42: add esp, 0000000Ch
  loc_00411B45: lea ecx, var_138
  loc_00411B4B: call [00401020h] ; __vbaFreeVar
  loc_00411B51: lea eax, var_84
  loc_00411B57: push eax
  loc_00411B58: call [00401044h] ; __vbaStrErrVarCopy
  loc_00411B5E: mov edx, eax
  loc_00411B60: lea ecx, var_C8
  loc_00411B66: call [004011D0h] ; __vbaStrMove
  loc_00411B6C: push eax
  loc_00411B6D: push 00406464h ; "MC"
  loc_00411B72: call [004010DCh] ; __vbaStrCmp
  loc_00411B78: neg eax
  loc_00411B7A: sbb eax, eax
  loc_00411B7C: neg eax
  loc_00411B7E: neg eax
  loc_00411B80: mov var_2C0, ax
  loc_00411B87: lea ecx, var_C8
  loc_00411B8D: call [004011F4h] ; __vbaFreeStr
  loc_00411B93: movsx ecx, var_2C0
  loc_00411B9A: test ecx, ecx
  loc_00411B9C: jz 00411DA1h
  loc_00411BA2: mov var_160, 80020004h
  loc_00411BAC: mov var_168, 0000000Ah
  loc_00411BB6: mov var_150, 80020004h
  loc_00411BC0: mov var_158, 0000000Ah
  loc_00411BCA: mov var_250, 004050E8h ; "IMT LampElectrical Probing"
  loc_00411BD4: mov var_258, 00000008h
  loc_00411BDE: lea edx, var_258
  loc_00411BE4: lea ecx, var_148
  loc_00411BEA: call [004011B4h] ; __vbaVarDup
  loc_00411BF0: push 00406470h ; "Prober command '"
  loc_00411BF5: push 00406A84h ; "SP2X0Y0"
  loc_00411BFA: call [00401050h] ; __vbaStrCat
  loc_00411C00: mov edx, eax
  loc_00411C02: lea ecx, var_C8
  loc_00411C08: call [004011D0h] ; __vbaStrMove
  loc_00411C0E: push eax
  loc_00411C0F: push 00406498h ; "' failed to return 'MC', instead said:"
  loc_00411C14: call [00401050h] ; __vbaStrCat
  loc_00411C1A: mov edx, eax
  loc_00411C1C: lea ecx, var_CC
  loc_00411C22: call [004011D0h] ; __vbaStrMove
  loc_00411C28: push eax
  loc_00411C29: push 004054D8h ; vbCrLf
  loc_00411C2E: call [00401050h] ; __vbaStrCat
  loc_00411C34: mov edx, eax
  loc_00411C36: lea ecx, var_D0
  loc_00411C3C: call [004011D0h] ; __vbaStrMove
  loc_00411C42: push eax
  loc_00411C43: lea edx, var_84
  loc_00411C49: push edx
  loc_00411C4A: call [00401044h] ; __vbaStrErrVarCopy
  loc_00411C50: mov edx, eax
  loc_00411C52: lea ecx, var_D4
  loc_00411C58: call [004011D0h] ; __vbaStrMove
  loc_00411C5E: push eax
  loc_00411C5F: call [00401050h] ; __vbaStrCat
  loc_00411C65: mov edx, eax
  loc_00411C67: lea ecx, var_D8
  loc_00411C6D: call [004011D0h] ; __vbaStrMove
  loc_00411C73: push eax
  loc_00411C74: push 004054D8h ; vbCrLf
  loc_00411C79: call [00401050h] ; __vbaStrCat
  loc_00411C7F: mov edx, eax
  loc_00411C81: lea ecx, var_DC
  loc_00411C87: call [004011D0h] ; __vbaStrMove
  loc_00411C8D: push eax
  loc_00411C8E: push 004064ECh ; "Continue anyway?"
  loc_00411C93: call [00401050h] ; __vbaStrCat
  loc_00411C99: mov var_130, eax
  loc_00411C9F: mov var_138, 00000008h
  loc_00411CA9: lea eax, var_168
  loc_00411CAF: push eax
  loc_00411CB0: lea ecx, var_158
  loc_00411CB6: push ecx
  loc_00411CB7: lea edx, var_148
  loc_00411CBD: push edx
  loc_00411CBE: push 00000004h
  loc_00411CC0: lea eax, var_138
  loc_00411CC6: push eax
  loc_00411CC7: call [00401084h] ; rtcMsgBox
  loc_00411CCD: mov ecx, eax
  loc_00411CCF: call [004010ECh] ; __vbaI2I4
  loc_00411CD5: mov var_18, ax
  loc_00411CD9: lea ecx, var_DC
  loc_00411CDF: push ecx
  loc_00411CE0: lea edx, var_D8
  loc_00411CE6: push edx
  loc_00411CE7: lea eax, var_D4
  loc_00411CED: push eax
  loc_00411CEE: lea ecx, var_D0
  loc_00411CF4: push ecx
  loc_00411CF5: lea edx, var_CC
  loc_00411CFB: push edx
  loc_00411CFC: lea eax, var_C8
  loc_00411D02: push eax
  loc_00411D03: push 00000006h
  loc_00411D05: call [00401180h] ; __vbaFreeStrList
  loc_00411D0B: add esp, 0000001Ch
  loc_00411D0E: lea ecx, var_168
  loc_00411D14: push ecx
  loc_00411D15: lea edx, var_158
  loc_00411D1B: push edx
  loc_00411D1C: lea eax, var_148
  loc_00411D22: push eax
  loc_00411D23: lea ecx, var_138
  loc_00411D29: push ecx
  loc_00411D2A: push 00000004h
  loc_00411D2C: call [00401038h] ; __vbaFreeVarList
  loc_00411D32: add esp, 00000014h
  loc_00411D35: movsx edx, var_18
  loc_00411D39: cmp edx, 00000007h
  loc_00411D3C: jnz 00411DA1h
  loc_00411D3E: lea eax, var_138
  loc_00411D44: push eax
  loc_00411D45: mov ecx, Me
  loc_00411D48: mov edx, [ecx]
  loc_00411D4A: mov eax, Me
  loc_00411D4D: push eax
  loc_00411D4E: call [edx+00000704h]
  loc_00411D54: mov var_2C0, eax
  loc_00411D5A: cmp var_2C0, 00000000h
  loc_00411D61: jge 00411D86h
  loc_00411D63: push 00000704h
  loc_00411D68: push 0040579Ch ; "#]=VｫoyAｷ ;ﾑs：ﾚLabel12"
  loc_00411D6D: mov ecx, Me
  loc_00411D70: push ecx
  loc_00411D71: mov edx, var_2C0
  loc_00411D77: push edx
  loc_00411D78: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00411D7E: mov var_518, eax
  loc_00411D84: jmp 00411D90h
  loc_00411D86: mov var_518, 00000000h
  loc_00411D90: lea ecx, var_138
  loc_00411D96: call [00401020h] ; __vbaFreeVar
  loc_00411D9C: jmp 0041489Fh
  loc_00411DA1: mov eax, Me
  loc_00411DA4: mov ecx, [eax]
  loc_00411DA6: mov edx, Me
  loc_00411DA9: push edx
  loc_00411DAA: call [ecx+00000370h]
  loc_00411DB0: push eax
  loc_00411DB1: lea eax, var_118
  loc_00411DB7: push eax
  loc_00411DB8: call [00401080h] ; __vbaObjSet
  loc_00411DBE: mov var_2C0, eax
  loc_00411DC4: lea ecx, var_28C
  loc_00411DCA: push ecx
  loc_00411DCB: mov edx, var_2C0
  loc_00411DD1: mov eax, [edx]
  loc_00411DD3: mov ecx, var_2C0
  loc_00411DD9: push ecx
  loc_00411DDA: call [eax+000000F0h]
  loc_00411DE0: fnclex
  loc_00411DE2: mov var_2C4, eax
  loc_00411DE8: cmp var_2C4, 00000000h
  loc_00411DEF: jge 00411E17h
  loc_00411DF1: push 000000F0h
  loc_00411DF6: push 004055DCh
  loc_00411DFB: mov edx, var_2C0
  loc_00411E01: push edx
  loc_00411E02: mov eax, var_2C4
  loc_00411E08: push eax
  loc_00411E09: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00411E0F: mov var_51C, eax
  loc_00411E15: jmp 00411E21h
  loc_00411E17: mov var_51C, 00000000h
  loc_00411E21: mov var_130, 00000000h
  loc_00411E2B: mov var_138, 00000002h
  loc_00411E35: mov ecx, Me
  loc_00411E38: mov edx, [ecx+0000003Ch]
  loc_00411E3B: push edx
  loc_00411E3C: lea eax, var_C4
  loc_00411E42: push eax
  loc_00411E43: call [004011A4h] ; __vbaAryLock
  loc_00411E49: cmp var_C4, 00000000h
  loc_00411E50: jz 00411EAEh
  loc_00411E52: mov ecx, var_C4
  loc_00411E58: cmp [ecx], 0001h
  loc_00411E5C: jnz 00411EAEh
  loc_00411E5E: movsx edx, var_28C
  loc_00411E65: mov eax, var_C4
  loc_00411E6B: sub edx, [eax+00000014h]
  loc_00411E6E: mov var_2C8, edx
  loc_00411E74: mov ecx, var_C4
  loc_00411E7A: mov edx, var_2C8
  loc_00411E80: cmp edx, [ecx+00000010h]
  loc_00411E83: jae 00411E91h
  loc_00411E85: mov var_520, 00000000h
  loc_00411E8F: jmp 00411E9Dh
  loc_00411E91: call [004010D8h] ; __vbaGenerateBoundsError
  loc_00411E97: mov var_520, eax
  loc_00411E9D: mov eax, var_2C8
  loc_00411EA3: shl eax, 02h
  loc_00411EA6: mov var_524, eax
  loc_00411EAC: jmp 00411EBAh
  loc_00411EAE: call [004010D8h] ; __vbaGenerateBoundsError
  loc_00411EB4: mov var_524, eax
  loc_00411EBA: mov ecx, var_C4
  loc_00411EC0: mov edx, [ecx+0000000Ch]
  loc_00411EC3: add edx, var_524
  loc_00411EC9: mov var_250, edx
  loc_00411ECF: mov var_258, 00004003h
  loc_00411ED9: lea eax, var_138
  loc_00411EDF: push eax
  loc_00411EE0: lea ecx, var_258
  loc_00411EE6: push ecx
  loc_00411EE7: call 0041DC40h
  loc_00411EEC: fstp real8 ptr var_2AC
  loc_00411EF2: lea edx, var_C4
  loc_00411EF8: push edx
  loc_00411EF9: call [004011E8h] ; __vbaAryUnlock
  loc_00411EFF: mov eax, var_2AC
  loc_00411F05: mov var_54, eax
  loc_00411F08: mov ecx, var_2A8
  loc_00411F0E: mov var_50, ecx
  loc_00411F11: lea ecx, var_118
  loc_00411F17: call [004011F0h] ; __vbaFreeObj
  loc_00411F1D: lea ecx, var_138
  loc_00411F23: call [00401020h] ; __vbaFreeVar
  loc_00411F29: mov edx, Me
  loc_00411F2C: mov eax, [edx]
  loc_00411F2E: mov ecx, Me
  loc_00411F31: push ecx
  loc_00411F32: call [eax+00000370h]
  loc_00411F38: push eax
  loc_00411F39: lea edx, var_118
  loc_00411F3F: push edx
  loc_00411F40: call [00401080h] ; __vbaObjSet
  loc_00411F46: mov var_2C0, eax
  loc_00411F4C: lea eax, var_28C
  loc_00411F52: push eax
  loc_00411F53: mov ecx, var_2C0
  loc_00411F59: mov edx, [ecx]
  loc_00411F5B: mov eax, var_2C0
  loc_00411F61: push eax
  loc_00411F62: call [edx+000000F0h]
  loc_00411F68: fnclex
  loc_00411F6A: mov var_2C4, eax
  loc_00411F70: cmp var_2C4, 00000000h
  loc_00411F77: jge 00411F9Fh
  loc_00411F79: push 000000F0h
  loc_00411F7E: push 004055DCh
  loc_00411F83: mov ecx, var_2C0
  loc_00411F89: push ecx
  loc_00411F8A: mov edx, var_2C4
  loc_00411F90: push edx
  loc_00411F91: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00411F97: mov var_528, eax
  loc_00411F9D: jmp 00411FA9h
  loc_00411F9F: mov var_528, 00000000h
  loc_00411FA9: mov var_130, 00000000h
  loc_00411FB3: mov var_138, 00000002h
  loc_00411FBD: mov eax, Me
  loc_00411FC0: mov ecx, [eax+00000044h]
  loc_00411FC3: push ecx
  loc_00411FC4: lea edx, var_C4
  loc_00411FCA: push edx
  loc_00411FCB: call [004011A4h] ; __vbaAryLock
  loc_00411FD1: cmp var_C4, 00000000h
  loc_00411FD8: jz 00412036h
  loc_00411FDA: mov eax, var_C4
  loc_00411FE0: cmp [eax], 0001h
  loc_00411FE4: jnz 00412036h
  loc_00411FE6: movsx ecx, var_28C
  loc_00411FED: mov edx, var_C4
  loc_00411FF3: sub ecx, [edx+00000014h]
  loc_00411FF6: mov var_2C8, ecx
  loc_00411FFC: mov eax, var_C4
  loc_00412002: mov ecx, var_2C8
  loc_00412008: cmp ecx, [eax+00000010h]
  loc_0041200B: jae 00412019h
  loc_0041200D: mov var_52C, 00000000h
  loc_00412017: jmp 00412025h
  loc_00412019: call [004010D8h] ; __vbaGenerateBoundsError
  loc_0041201F: mov var_52C, eax
  loc_00412025: mov edx, var_2C8
  loc_0041202B: shl edx, 02h
  loc_0041202E: mov var_530, edx
  loc_00412034: jmp 00412042h
  loc_00412036: call [004010D8h] ; __vbaGenerateBoundsError
  loc_0041203C: mov var_530, eax
  loc_00412042: mov eax, var_C4
  loc_00412048: mov ecx, [eax+0000000Ch]
  loc_0041204B: add ecx, var_530
  loc_00412051: mov var_250, ecx
  loc_00412057: mov var_258, 00004003h
  loc_00412061: lea edx, var_138
  loc_00412067: push edx
  loc_00412068: lea eax, var_258
  loc_0041206E: push eax
  loc_0041206F: call 0041DC40h
  loc_00412074: fstp real8 ptr var_2AC
  loc_0041207A: lea ecx, var_C4
  loc_00412080: push ecx
  loc_00412081: call [004011E8h] ; __vbaAryUnlock
  loc_00412087: mov edx, var_2AC
  loc_0041208D: mov var_90, edx
  loc_00412093: mov eax, var_2A8
  loc_00412099: mov var_8C, eax
  loc_0041209F: lea ecx, var_118
  loc_004120A5: call [004011F0h] ; __vbaFreeObj
  loc_004120AB: lea ecx, var_138
  loc_004120B1: call [00401020h] ; __vbaFreeVar
  loc_004120B7: mov ecx, Me
  loc_004120BA: movsx edx, [ecx+0000005Eh]
  loc_004120BE: test edx, edx
  loc_004120C0: jz 00412125h
  loc_004120C2: lea eax, var_138
  loc_004120C8: push eax
  loc_004120C9: mov ecx, Me
  loc_004120CC: mov edx, [ecx]
  loc_004120CE: mov eax, Me
  loc_004120D1: push eax
  loc_004120D2: call [edx+00000704h]
  loc_004120D8: mov var_2C0, eax
  loc_004120DE: cmp var_2C0, 00000000h
  loc_004120E5: jge 0041210Ah
  loc_004120E7: push 00000704h
  loc_004120EC: push 0040579Ch ; "#]=VｫoyAｷ ;ﾑs：ﾚLabel12"
  loc_004120F1: mov ecx, Me
  loc_004120F4: push ecx
  loc_004120F5: mov edx, var_2C0
  loc_004120FB: push edx
  loc_004120FC: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00412102: mov var_534, eax
  loc_00412108: jmp 00412114h
  loc_0041210A: mov var_534, 00000000h
  loc_00412114: lea ecx, var_138
  loc_0041211A: call [00401020h] ; __vbaFreeVar
  loc_00412120: jmp 0041489Fh
  loc_00412125: fld real8 ptr var_54
  loc_00412128: fcomp real8 ptr [00401288h]
  loc_0041212E: fnstsw ax
  loc_00412130: test ah, 40h
  loc_00412133: jz 00412141h
  loc_00412135: mov var_538, 00000001h
  loc_0041213F: jmp 0041214Bh
  loc_00412141: mov var_538, 00000000h
  loc_0041214B: fld real8 ptr var_90
  loc_00412151: fcomp real8 ptr [00401288h]
  loc_00412157: fnstsw ax
  loc_00412159: test ah, 40h
  loc_0041215C: jz 0041216Ah
  loc_0041215E: mov var_53C, 00000001h
  loc_00412168: jmp 00412174h
  loc_0041216A: mov var_53C, 00000000h
  loc_00412174: mov eax, var_538
  loc_0041217A: and eax, var_53C
  loc_00412180: test eax, eax
  loc_00412182: jnz 004126B5h
  loc_00412188: mov ecx, Me
  loc_0041218B: mov edx, [ecx]
  loc_0041218D: mov eax, Me
  loc_00412190: push eax
  loc_00412191: call [edx+0000039Ch]
  loc_00412197: push eax
  loc_00412198: lea ecx, var_11C
  loc_0041219E: push ecx
  loc_0041219F: call [00401080h] ; __vbaObjSet
  loc_004121A5: mov var_2C8, eax
  loc_004121AB: mov edx, Me
  loc_004121AE: mov eax, [edx]
  loc_004121B0: mov ecx, Me
  loc_004121B3: push ecx
  loc_004121B4: call [eax+00000370h]
  loc_004121BA: push eax
  loc_004121BB: lea edx, var_118
  loc_004121C1: push edx
  loc_004121C2: call [00401080h] ; __vbaObjSet
  loc_004121C8: mov var_2C0, eax
  loc_004121CE: lea eax, var_C8
  loc_004121D4: push eax
  loc_004121D5: mov ecx, var_2C0
  loc_004121DB: mov edx, [ecx]
  loc_004121DD: mov eax, var_2C0
  loc_004121E3: push eax
  loc_004121E4: call [edx+000000A8h]
  loc_004121EA: fnclex
  loc_004121EC: mov var_2C4, eax
  loc_004121F2: cmp var_2C4, 00000000h
  loc_004121F9: jge 00412221h
  loc_004121FB: push 000000A8h
  loc_00412200: push 004055DCh
  loc_00412205: mov ecx, var_2C0
  loc_0041220B: push ecx
  loc_0041220C: mov edx, var_2C4
  loc_00412212: push edx
  loc_00412213: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00412219: mov var_540, eax
  loc_0041221F: jmp 0041222Bh
  loc_00412221: mov var_540, 00000000h
  loc_0041222B: push 00405FB4h ; "Moving to "
  loc_00412230: mov eax, var_C8
  loc_00412236: push eax
  loc_00412237: call [00401050h] ; __vbaStrCat
  loc_0041223D: mov edx, eax
  loc_0041223F: lea ecx, var_CC
  loc_00412245: call [004011D0h] ; __vbaStrMove
  loc_0041224B: push eax
  loc_0041224C: mov ecx, var_2C8
  loc_00412252: mov edx, [ecx]
  loc_00412254: mov eax, var_2C8
  loc_0041225A: push eax
  loc_0041225B: call [edx+00000054h]
  loc_0041225E: fnclex
  loc_00412260: mov var_2CC, eax
  loc_00412266: cmp var_2CC, 00000000h
  loc_0041226D: jge 00412292h
  loc_0041226F: push 00000054h
  loc_00412271: push 0040575Ch
  loc_00412276: mov ecx, var_2C8
  loc_0041227C: push ecx
  loc_0041227D: mov edx, var_2CC
  loc_00412283: push edx
  loc_00412284: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041228A: mov var_544, eax
  loc_00412290: jmp 0041229Ch
  loc_00412292: mov var_544, 00000000h
  loc_0041229C: lea eax, var_CC
  loc_004122A2: push eax
  loc_004122A3: lea ecx, var_C8
  loc_004122A9: push ecx
  loc_004122AA: push 00000002h
  loc_004122AC: call [00401180h] ; __vbaFreeStrList
  loc_004122B2: add esp, 0000000Ch
  loc_004122B5: lea edx, var_11C
  loc_004122BB: push edx
  loc_004122BC: lea eax, var_118
  loc_004122C2: push eax
  loc_004122C3: push 00000002h
  loc_004122C5: call [00401040h] ; __vbaFreeObjList
  loc_004122CB: add esp, 0000000Ch
  loc_004122CE: call [004010A0h] ; rtcDoEvents
  loc_004122D4: mov var_250, 00406440h ; "MMX"
  loc_004122DE: mov var_258, 00000008h
  loc_004122E8: mov ecx, var_50
  loc_004122EB: push ecx
  loc_004122EC: mov edx, var_54
  loc_004122EF: push edx
  loc_004122F0: call [00401104h] ; __vbaStrR8
  loc_004122F6: mov var_130, eax
  loc_004122FC: mov var_138, 00000008h
  loc_00412306: lea eax, var_138
  loc_0041230C: push eax
  loc_0041230D: lea ecx, var_148
  loc_00412313: push ecx
  loc_00412314: call [004010A4h] ; rtcTrimVar
  loc_0041231A: mov var_260, 0040644Ch ; "Y"
  loc_00412324: mov var_268, 00000008h
  loc_0041232E: mov edx, var_8C
  loc_00412334: push edx
  loc_00412335: mov eax, var_90
  loc_0041233B: push eax
  loc_0041233C: call [00401104h] ; __vbaStrR8
  loc_00412342: mov var_170, eax
  loc_00412348: mov var_178, 00000008h
  loc_00412352: lea ecx, var_178
  loc_00412358: push ecx
  loc_00412359: lea edx, var_188
  loc_0041235F: push edx
  loc_00412360: call [004010A4h] ; rtcTrimVar
  loc_00412366: lea eax, var_258
  loc_0041236C: push eax
  loc_0041236D: lea ecx, var_148
  loc_00412373: push ecx
  loc_00412374: lea edx, var_158
  loc_0041237A: push edx
  loc_0041237B: call [004011ACh] ; __vbaVarAdd
  loc_00412381: push eax
  loc_00412382: lea eax, var_268
  loc_00412388: push eax
  loc_00412389: lea ecx, var_168
  loc_0041238F: push ecx
  loc_00412390: call [004011ACh] ; __vbaVarAdd
  loc_00412396: push eax
  loc_00412397: lea edx, var_188
  loc_0041239D: push edx
  loc_0041239E: lea eax, var_198
  loc_004123A4: push eax
  loc_004123A5: call [004011ACh] ; __vbaVarAdd
  loc_004123AB: push eax
  loc_004123AC: call [00401030h] ; __vbaStrVarMove
  loc_004123B2: mov edx, eax
  loc_004123B4: lea ecx, var_58
  loc_004123B7: call [004011D0h] ; __vbaStrMove
  loc_004123BD: lea ecx, var_198
  loc_004123C3: push ecx
  loc_004123C4: lea edx, var_188
  loc_004123CA: push edx
  loc_004123CB: lea eax, var_168
  loc_004123D1: push eax
  loc_004123D2: lea ecx, var_178
  loc_004123D8: push ecx
  loc_004123D9: lea edx, var_158
  loc_004123DF: push edx
  loc_004123E0: lea eax, var_148
  loc_004123E6: push eax
  loc_004123E7: lea ecx, var_138
  loc_004123ED: push ecx
  loc_004123EE: push 00000007h
  loc_004123F0: call [00401038h] ; __vbaFreeVarList
  loc_004123F6: add esp, 00000020h
  loc_004123F9: mov var_130, FFFFFFFFh
  loc_00412403: mov var_138, 0000000Bh
  loc_0041240D: mov edx, 00406454h ; "2001X"
  loc_00412412: lea ecx, var_C8
  loc_00412418: call [00401178h] ; __vbaStrCopy
  loc_0041241E: lea edx, var_138
  loc_00412424: push edx
  loc_00412425: lea eax, var_58
  loc_00412428: push eax
  loc_00412429: lea ecx, var_C8
  loc_0041242F: push ecx
  loc_00412430: lea edx, var_148
  loc_00412436: push edx
  loc_00412437: call 0041CA40h
  loc_0041243C: lea edx, var_148
  loc_00412442: lea ecx, var_84
  loc_00412448: call [00401014h] ; __vbaVarMove
  loc_0041244E: lea ecx, var_C8
  loc_00412454: call [004011F4h] ; __vbaFreeStr
  loc_0041245A: lea ecx, var_138
  loc_00412460: call [00401020h] ; __vbaFreeVar
  loc_00412466: lea eax, var_84
  loc_0041246C: push eax
  loc_0041246D: call [00401044h] ; __vbaStrErrVarCopy
  loc_00412473: mov edx, eax
  loc_00412475: lea ecx, var_C8
  loc_0041247B: call [004011D0h] ; __vbaStrMove
  loc_00412481: push eax
  loc_00412482: push 00406464h ; "MC"
  loc_00412487: call [004010DCh] ; __vbaStrCmp
  loc_0041248D: neg eax
  loc_0041248F: sbb eax, eax
  loc_00412491: neg eax
  loc_00412493: neg eax
  loc_00412495: mov var_2C0, ax
  loc_0041249C: lea ecx, var_C8
  loc_004124A2: call [004011F4h] ; __vbaFreeStr
  loc_004124A8: movsx ecx, var_2C0
  loc_004124AF: test ecx, ecx
  loc_004124B1: jz 004126B5h
  loc_004124B7: mov var_160, 80020004h
  loc_004124C1: mov var_168, 0000000Ah
  loc_004124CB: mov var_150, 80020004h
  loc_004124D5: mov var_158, 0000000Ah
  loc_004124DF: mov var_250, 004050E8h ; "IMT LampElectrical Probing"
  loc_004124E9: mov var_258, 00000008h
  loc_004124F3: lea edx, var_258
  loc_004124F9: lea ecx, var_148
  loc_004124FF: call [004011B4h] ; __vbaVarDup
  loc_00412505: push 00406470h ; "Prober command '"
  loc_0041250A: mov edx, var_58
  loc_0041250D: push edx
  loc_0041250E: call [00401050h] ; __vbaStrCat
  loc_00412514: mov edx, eax
  loc_00412516: lea ecx, var_C8
  loc_0041251C: call [004011D0h] ; __vbaStrMove
  loc_00412522: push eax
  loc_00412523: push 00406498h ; "' failed to return 'MC', instead said:"
  loc_00412528: call [00401050h] ; __vbaStrCat
  loc_0041252E: mov edx, eax
  loc_00412530: lea ecx, var_CC
  loc_00412536: call [004011D0h] ; __vbaStrMove
  loc_0041253C: push eax
  loc_0041253D: push 004054D8h ; vbCrLf
  loc_00412542: call [00401050h] ; __vbaStrCat
  loc_00412548: mov edx, eax
  loc_0041254A: lea ecx, var_D0
  loc_00412550: call [004011D0h] ; __vbaStrMove
  loc_00412556: push eax
  loc_00412557: lea eax, var_84
  loc_0041255D: push eax
  loc_0041255E: call [00401044h] ; __vbaStrErrVarCopy
  loc_00412564: mov edx, eax
  loc_00412566: lea ecx, var_D4
  loc_0041256C: call [004011D0h] ; __vbaStrMove
  loc_00412572: push eax
  loc_00412573: call [00401050h] ; __vbaStrCat
  loc_00412579: mov edx, eax
  loc_0041257B: lea ecx, var_D8
  loc_00412581: call [004011D0h] ; __vbaStrMove
  loc_00412587: push eax
  loc_00412588: push 004054D8h ; vbCrLf
  loc_0041258D: call [00401050h] ; __vbaStrCat
  loc_00412593: mov edx, eax
  loc_00412595: lea ecx, var_DC
  loc_0041259B: call [004011D0h] ; __vbaStrMove
  loc_004125A1: push eax
  loc_004125A2: push 004064ECh ; "Continue anyway?"
  loc_004125A7: call [00401050h] ; __vbaStrCat
  loc_004125AD: mov var_130, eax
  loc_004125B3: mov var_138, 00000008h
  loc_004125BD: lea ecx, var_168
  loc_004125C3: push ecx
  loc_004125C4: lea edx, var_158
  loc_004125CA: push edx
  loc_004125CB: lea eax, var_148
  loc_004125D1: push eax
  loc_004125D2: push 00000004h
  loc_004125D4: lea ecx, var_138
  loc_004125DA: push ecx
  loc_004125DB: call [00401084h] ; rtcMsgBox
  loc_004125E1: mov ecx, eax
  loc_004125E3: call [004010ECh] ; __vbaI2I4
  loc_004125E9: mov var_18, ax
  loc_004125ED: lea edx, var_DC
  loc_004125F3: push edx
  loc_004125F4: lea eax, var_D8
  loc_004125FA: push eax
  loc_004125FB: lea ecx, var_D4
  loc_00412601: push ecx
  loc_00412602: lea edx, var_D0
  loc_00412608: push edx
  loc_00412609: lea eax, var_CC
  loc_0041260F: push eax
  loc_00412610: lea ecx, var_C8
  loc_00412616: push ecx
  loc_00412617: push 00000006h
  loc_00412619: call [00401180h] ; __vbaFreeStrList
  loc_0041261F: add esp, 0000001Ch
  loc_00412622: lea edx, var_168
  loc_00412628: push edx
  loc_00412629: lea eax, var_158
  loc_0041262F: push eax
  loc_00412630: lea ecx, var_148
  loc_00412636: push ecx
  loc_00412637: lea edx, var_138
  loc_0041263D: push edx
  loc_0041263E: push 00000004h
  loc_00412640: call [00401038h] ; __vbaFreeVarList
  loc_00412646: add esp, 00000014h
  loc_00412649: movsx eax, var_18
  loc_0041264D: cmp eax, 00000007h
  loc_00412650: jnz 004126B5h
  loc_00412652: lea ecx, var_138
  loc_00412658: push ecx
  loc_00412659: mov edx, Me
  loc_0041265C: mov eax, [edx]
  loc_0041265E: mov ecx, Me
  loc_00412661: push ecx
  loc_00412662: call [eax+00000704h]
  loc_00412668: mov var_2C0, eax
  loc_0041266E: cmp var_2C0, 00000000h
  loc_00412675: jge 0041269Ah
  loc_00412677: push 00000704h
  loc_0041267C: push 0040579Ch ; "#]=VｫoyAｷ ;ﾑs：ﾚLabel12"
  loc_00412681: mov edx, Me
  loc_00412684: push edx
  loc_00412685: mov eax, var_2C0
  loc_0041268B: push eax
  loc_0041268C: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00412692: mov var_548, eax
  loc_00412698: jmp 004126A4h
  loc_0041269A: mov var_548, 00000000h
  loc_004126A4: lea ecx, var_138
  loc_004126AA: call [00401020h] ; __vbaFreeVar
  loc_004126B0: jmp 0041489Fh
  loc_004126B5: jmp 0041276Bh
  loc_004126BA: mov ecx, Me
  loc_004126BD: mov edx, [ecx]
  loc_004126BF: mov eax, Me
  loc_004126C2: push eax
  loc_004126C3: call [edx+00000370h]
  loc_004126C9: push eax
  loc_004126CA: lea ecx, var_118
  loc_004126D0: push ecx
  loc_004126D1: call [00401080h] ; __vbaObjSet
  loc_004126D7: mov var_2C0, eax
  loc_004126DD: lea edx, var_C8
  loc_004126E3: push edx
  loc_004126E4: mov eax, var_2C0
  loc_004126EA: mov ecx, [eax]
  loc_004126EC: mov edx, var_2C0
  loc_004126F2: push edx
  loc_004126F3: call [ecx+000000A8h]
  loc_004126F9: fnclex
  loc_004126FB: mov var_2C4, eax
  loc_00412701: cmp var_2C4, 00000000h
  loc_00412708: jge 00412730h
  loc_0041270A: push 000000A8h
  loc_0041270F: push 004055DCh
  loc_00412714: mov eax, var_2C0
  loc_0041271A: push eax
  loc_0041271B: mov ecx, var_2C4
  loc_00412721: push ecx
  loc_00412722: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00412728: mov var_54C, eax
  loc_0041272E: jmp 0041273Ah
  loc_00412730: mov var_54C, 00000000h
  loc_0041273A: mov edx, var_C8
  loc_00412740: mov var_358, edx
  loc_00412746: mov var_C8, 00000000h
  loc_00412750: mov edx, var_358
  loc_00412756: lea ecx, var_40
  loc_00412759: call [004011D0h] ; __vbaStrMove
  loc_0041275F: lea ecx, var_118
  loc_00412765: call [004011F0h] ; __vbaFreeObj
  loc_0041276B: mov edx, 00406938h ; "Initializing Keithley 2400"
  loc_00412770: lea ecx, var_C8
  loc_00412776: call [00401178h] ; __vbaStrCopy
  loc_0041277C: lea eax, var_138
  loc_00412782: push eax
  loc_00412783: lea ecx, var_C8
  loc_00412789: push ecx
  loc_0041278A: mov edx, Me
  loc_0041278D: mov eax, [edx]
  loc_0041278F: mov ecx, Me
  loc_00412792: push ecx
  loc_00412793: call [eax+00000700h]
  loc_00412799: mov var_2C0, eax
  loc_0041279F: cmp var_2C0, 00000000h
  loc_004127A6: jge 004127CBh
  loc_004127A8: push 00000700h
  loc_004127AD: push 0040579Ch ; "#]=VｫoyAｷ ;ﾑs：ﾚLabel12"
  loc_004127B2: mov edx, Me
  loc_004127B5: push edx
  loc_004127B6: mov eax, var_2C0
  loc_004127BC: push eax
  loc_004127BD: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004127C3: mov var_550, eax
  loc_004127C9: jmp 004127D5h
  loc_004127CB: mov var_550, 00000000h
  loc_004127D5: lea ecx, var_C8
  loc_004127DB: call [004011F4h] ; __vbaFreeStr
  loc_004127E1: lea ecx, var_138
  loc_004127E7: call [00401020h] ; __vbaFreeVar
  loc_004127ED: mov ecx, Me
  loc_004127F0: mov edx, [ecx]
  loc_004127F2: mov eax, Me
  loc_004127F5: push eax
  loc_004127F6: call [edx+00000304h]
  loc_004127FC: push eax
  loc_004127FD: lea ecx, var_118
  loc_00412803: push ecx
  loc_00412804: call [00401080h] ; __vbaObjSet
  loc_0041280A: mov var_2C0, eax
  loc_00412810: lea edx, var_C8
  loc_00412816: push edx
  loc_00412817: mov eax, var_2C0
  loc_0041281D: mov ecx, [eax]
  loc_0041281F: mov edx, var_2C0
  loc_00412825: push edx
  loc_00412826: call [ecx+000000A0h]
  loc_0041282C: fnclex
  loc_0041282E: mov var_2C4, eax
  loc_00412834: cmp var_2C4, 00000000h
  loc_0041283B: jge 00412863h
  loc_0041283D: push 000000A0h
  loc_00412842: push 00405398h
  loc_00412847: mov eax, var_2C0
  loc_0041284D: push eax
  loc_0041284E: mov ecx, var_2C4
  loc_00412854: push ecx
  loc_00412855: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041285B: mov var_554, eax
  loc_00412861: jmp 0041286Dh
  loc_00412863: mov var_554, 00000000h
  loc_0041286D: mov edx, Me
  loc_00412870: mov eax, [edx]
  loc_00412872: mov ecx, Me
  loc_00412875: push ecx
  loc_00412876: call [eax+00000308h]
  loc_0041287C: push eax
  loc_0041287D: lea edx, var_11C
  loc_00412883: push edx
  loc_00412884: call [00401080h] ; __vbaObjSet
  loc_0041288A: mov var_2C8, eax
  loc_00412890: lea eax, var_CC
  loc_00412896: push eax
  loc_00412897: mov ecx, var_2C8
  loc_0041289D: mov edx, [ecx]
  loc_0041289F: mov eax, var_2C8
  loc_004128A5: push eax
  loc_004128A6: call [edx+000000A0h]
  loc_004128AC: fnclex
  loc_004128AE: mov var_2CC, eax
  loc_004128B4: cmp var_2CC, 00000000h
  loc_004128BB: jge 004128E3h
  loc_004128BD: push 000000A0h
  loc_004128C2: push 00405398h
  loc_004128C7: mov ecx, var_2C8
  loc_004128CD: push ecx
  loc_004128CE: mov edx, var_2CC
  loc_004128D4: push edx
  loc_004128D5: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004128DB: mov var_558, eax
  loc_004128E1: jmp 004128EDh
  loc_004128E3: mov var_558, 00000000h
  loc_004128ED: mov eax, var_CC
  loc_004128F3: mov var_35C, eax
  loc_004128F9: mov var_CC, 00000000h
  loc_00412903: mov edx, var_35C
  loc_00412909: lea ecx, var_D4
  loc_0041290F: call [004011D0h] ; __vbaStrMove
  loc_00412915: mov ecx, var_C8
  loc_0041291B: mov var_360, ecx
  loc_00412921: mov var_C8, 00000000h
  loc_0041292B: mov edx, var_360
  loc_00412931: lea ecx, var_D0
  loc_00412937: call [004011D0h] ; __vbaStrMove
  loc_0041293D: lea edx, var_D4
  loc_00412943: push edx
  loc_00412944: lea eax, var_D0
  loc_0041294A: push eax
  loc_0041294B: lea ecx, var_138
  loc_00412951: push ecx
  loc_00412952: call 00420200h
  loc_00412957: lea edx, var_D4
  loc_0041295D: push edx
  loc_0041295E: lea eax, var_D0
  loc_00412964: push eax
  loc_00412965: push 00000002h
  loc_00412967: call [00401180h] ; __vbaFreeStrList
  loc_0041296D: add esp, 0000000Ch
  loc_00412970: lea ecx, var_11C
  loc_00412976: push ecx
  loc_00412977: lea edx, var_118
  loc_0041297D: push edx
  loc_0041297E: push 00000002h
  loc_00412980: call [00401040h] ; __vbaFreeObjList
  loc_00412986: add esp, 0000000Ch
  loc_00412989: lea ecx, var_138
  loc_0041298F: call [00401020h] ; __vbaFreeVar
  loc_00412995: mov eax, Me
  loc_00412998: movsx ecx, [eax+0000005Eh]
  loc_0041299C: test ecx, ecx
  loc_0041299E: jz 00412A03h
  loc_004129A0: lea edx, var_138
  loc_004129A6: push edx
  loc_004129A7: mov eax, Me
  loc_004129AA: mov ecx, [eax]
  loc_004129AC: mov edx, Me
  loc_004129AF: push edx
  loc_004129B0: call [ecx+00000704h]
  loc_004129B6: mov var_2C0, eax
  loc_004129BC: cmp var_2C0, 00000000h
  loc_004129C3: jge 004129E8h
  loc_004129C5: push 00000704h
  loc_004129CA: push 0040579Ch ; "#]=VｫoyAｷ ;ﾑs：ﾚLabel12"
  loc_004129CF: mov eax, Me
  loc_004129D2: push eax
  loc_004129D3: mov ecx, var_2C0
  loc_004129D9: push ecx
  loc_004129DA: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004129E0: mov var_55C, eax
  loc_004129E6: jmp 004129F2h
  loc_004129E8: mov var_55C, 00000000h
  loc_004129F2: lea ecx, var_138
  loc_004129F8: call [00401020h] ; __vbaFreeVar
  loc_004129FE: jmp 0041489Fh
  loc_00412A03: mov edx, 00406044h ; "Initializing Switches"
  loc_00412A08: lea ecx, var_C8
  loc_00412A0E: call [00401178h] ; __vbaStrCopy
  loc_00412A14: lea edx, var_138
  loc_00412A1A: push edx
  loc_00412A1B: lea eax, var_C8
  loc_00412A21: push eax
  loc_00412A22: mov ecx, Me
  loc_00412A25: mov edx, [ecx]
  loc_00412A27: mov eax, Me
  loc_00412A2A: push eax
  loc_00412A2B: call [edx+00000700h]
  loc_00412A31: mov var_2C0, eax
  loc_00412A37: cmp var_2C0, 00000000h
  loc_00412A3E: jge 00412A63h
  loc_00412A40: push 00000700h
  loc_00412A45: push 0040579Ch ; "#]=VｫoyAｷ ;ﾑs：ﾚLabel12"
  loc_00412A4A: mov ecx, Me
  loc_00412A4D: push ecx
  loc_00412A4E: mov edx, var_2C0
  loc_00412A54: push edx
  loc_00412A55: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00412A5B: mov var_560, eax
  loc_00412A61: jmp 00412A6Dh
  loc_00412A63: mov var_560, 00000000h
  loc_00412A6D: lea ecx, var_C8
  loc_00412A73: call [004011F4h] ; __vbaFreeStr
  loc_00412A79: lea ecx, var_138
  loc_00412A7F: call [00401020h] ; __vbaFreeVar
  loc_00412A85: lea eax, var_138
  loc_00412A8B: push eax
  loc_00412A8C: call 0041FE20h
  loc_00412A91: lea ecx, var_138
  loc_00412A97: call [00401020h] ; __vbaFreeVar
  loc_00412A9D: mov ecx, Me
  loc_00412AA0: mov edx, [ecx]
  loc_00412AA2: mov eax, Me
  loc_00412AA5: push eax
  loc_00412AA6: call [edx+0000030Ch]
  loc_00412AAC: push eax
  loc_00412AAD: lea ecx, var_118
  loc_00412AB3: push ecx
  loc_00412AB4: call [00401080h] ; __vbaObjSet
  loc_00412ABA: mov var_2C0, eax
  loc_00412AC0: lea edx, var_C8
  loc_00412AC6: push edx
  loc_00412AC7: mov eax, var_2C0
  loc_00412ACD: mov ecx, [eax]
  loc_00412ACF: mov edx, var_2C0
  loc_00412AD5: push edx
  loc_00412AD6: call [ecx+000000A0h]
  loc_00412ADC: fnclex
  loc_00412ADE: mov var_2C4, eax
  loc_00412AE4: cmp var_2C4, 00000000h
  loc_00412AEB: jge 00412B13h
  loc_00412AED: push 000000A0h
  loc_00412AF2: push 00405398h
  loc_00412AF7: mov eax, var_2C0
  loc_00412AFD: push eax
  loc_00412AFE: mov ecx, var_2C4
  loc_00412B04: push ecx
  loc_00412B05: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00412B0B: mov var_564, eax
  loc_00412B11: jmp 00412B1Dh
  loc_00412B13: mov var_564, 00000000h
  loc_00412B1D: mov edx, var_C8
  loc_00412B23: push edx
  loc_00412B24: call [0040117Ch] ; __vbaI4Str
  loc_00412B2A: mov var_74, eax
  loc_00412B2D: lea ecx, var_C8
  loc_00412B33: call [004011F4h] ; __vbaFreeStr
  loc_00412B39: lea ecx, var_118
  loc_00412B3F: call [004011F0h] ; __vbaFreeObj
  loc_00412B45: lea eax, var_314
  loc_00412B4B: push eax
  loc_00412B4C: call [00401138h] ; __vbaGosub
  loc_00412B52: test eax, eax
  loc_00412B54: jnz 00412B5Bh
  loc_00412B56: jmp 0041302Ch
  loc_00412B5B: mov ecx, Me
  loc_00412B5E: movsx edx, [ecx+0000005Eh]
  loc_00412B62: test edx, edx
  loc_00412B64: jz 00412CE1h
  loc_00412B6A: mov eax, Me
  loc_00412B6D: mov ecx, [eax]
  loc_00412B6F: mov edx, Me
  loc_00412B72: push edx
  loc_00412B73: call [ecx+00000368h]
  loc_00412B79: push eax
  loc_00412B7A: lea eax, var_118
  loc_00412B80: push eax
  loc_00412B81: call [00401080h] ; __vbaObjSet
  loc_00412B87: mov var_2C0, eax
  loc_00412B8D: lea ecx, var_28C
  loc_00412B93: push ecx
  loc_00412B94: mov edx, var_2C0
  loc_00412B9A: mov eax, [edx]
  loc_00412B9C: mov ecx, var_2C0
  loc_00412BA2: push ecx
  loc_00412BA3: call [eax+000000E0h]
  loc_00412BA9: fnclex
  loc_00412BAB: mov var_2C4, eax
  loc_00412BB1: cmp var_2C4, 00000000h
  loc_00412BB8: jge 00412BE0h
  loc_00412BBA: push 000000E0h
  loc_00412BBF: push 00405354h
  loc_00412BC4: mov edx, var_2C0
  loc_00412BCA: push edx
  loc_00412BCB: mov eax, var_2C4
  loc_00412BD1: push eax
  loc_00412BD2: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00412BD8: mov var_568, eax
  loc_00412BDE: jmp 00412BEAh
  loc_00412BE0: mov var_568, 00000000h
  loc_00412BEA: movsx ecx, var_28C
  loc_00412BF1: sub ecx, 00000001h
  loc_00412BF4: neg ecx
  loc_00412BF6: sbb ecx, ecx
  loc_00412BF8: inc ecx
  loc_00412BF9: neg ecx
  loc_00412BFB: mov var_2C8, cx
  loc_00412C02: lea ecx, var_118
  loc_00412C08: call [004011F0h] ; __vbaFreeObj
  loc_00412C0E: movsx edx, var_2C8
  loc_00412C15: test edx, edx
  loc_00412C17: jz 00412C7Eh
  loc_00412C19: lea eax, var_138
  loc_00412C1F: push eax
  loc_00412C20: lea ecx, var_A0
  loc_00412C26: push ecx
  loc_00412C27: mov edx, Me
  loc_00412C2A: mov eax, [edx]
  loc_00412C2C: mov ecx, Me
  loc_00412C2F: push ecx
  loc_00412C30: call [eax+00000708h]
  loc_00412C36: mov var_2C0, eax
  loc_00412C3C: cmp var_2C0, 00000000h
  loc_00412C43: jge 00412C68h
  loc_00412C45: push 00000708h
  loc_00412C4A: push 0040579Ch ; "#]=VｫoyAｷ ;ﾑs：ﾚLabel12"
  loc_00412C4F: mov edx, Me
  loc_00412C52: push edx
  loc_00412C53: mov eax, var_2C0
  loc_00412C59: push eax
  loc_00412C5A: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00412C60: mov var_56C, eax
  loc_00412C66: jmp 00412C72h
  loc_00412C68: mov var_56C, 00000000h
  loc_00412C72: lea ecx, var_138
  loc_00412C78: call [00401020h] ; __vbaFreeVar
  loc_00412C7E: lea ecx, var_138
  loc_00412C84: push ecx
  loc_00412C85: mov edx, Me
  loc_00412C88: mov eax, [edx]
  loc_00412C8A: mov ecx, Me
  loc_00412C8D: push ecx
  loc_00412C8E: call [eax+00000704h]
  loc_00412C94: mov var_2C0, eax
  loc_00412C9A: cmp var_2C0, 00000000h
  loc_00412CA1: jge 00412CC6h
  loc_00412CA3: push 00000704h
  loc_00412CA8: push 0040579Ch ; "#]=VｫoyAｷ ;ﾑs：ﾚLabel12"
  loc_00412CAD: mov edx, Me
  loc_00412CB0: push edx
  loc_00412CB1: mov eax, var_2C0
  loc_00412CB7: push eax
  loc_00412CB8: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00412CBE: mov var_570, eax
  loc_00412CC4: jmp 00412CD0h
  loc_00412CC6: mov var_570, 00000000h
  loc_00412CD0: lea ecx, var_138
  loc_00412CD6: call [00401020h] ; __vbaFreeVar
  loc_00412CDC: jmp 0041489Fh
  loc_00412CE1: mov ecx, Me
  loc_00412CE4: mov edx, [ecx]
  loc_00412CE6: mov eax, Me
  loc_00412CE9: push eax
  loc_00412CEA: call [edx+00000368h]
  loc_00412CF0: push eax
  loc_00412CF1: lea ecx, var_118
  loc_00412CF7: push ecx
  loc_00412CF8: call [00401080h] ; __vbaObjSet
  loc_00412CFE: mov var_2C0, eax
  loc_00412D04: lea edx, var_28C
  loc_00412D0A: push edx
  loc_00412D0B: mov eax, var_2C0
  loc_00412D11: mov ecx, [eax]
  loc_00412D13: mov edx, var_2C0
  loc_00412D19: push edx
  loc_00412D1A: call [ecx+000000E0h]
  loc_00412D20: fnclex
  loc_00412D22: mov var_2C4, eax
  loc_00412D28: cmp var_2C4, 00000000h
  loc_00412D2F: jge 00412D57h
  loc_00412D31: push 000000E0h
  loc_00412D36: push 00405354h
  loc_00412D3B: mov eax, var_2C0
  loc_00412D41: push eax
  loc_00412D42: mov ecx, var_2C4
  loc_00412D48: push ecx
  loc_00412D49: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00412D4F: mov var_574, eax
  loc_00412D55: jmp 00412D61h
  loc_00412D57: mov var_574, 00000000h
  loc_00412D61: movsx edx, var_28C
  loc_00412D68: sub edx, 00000001h
  loc_00412D6B: neg edx
  loc_00412D6D: sbb edx, edx
  loc_00412D6F: inc edx
  loc_00412D70: neg edx
  loc_00412D72: mov var_2C8, dx
  loc_00412D79: lea ecx, var_118
  loc_00412D7F: call [004011F0h] ; __vbaFreeObj
  loc_00412D85: movsx eax, var_2C8
  loc_00412D8C: test eax, eax
  loc_00412D8E: jz 00412EC9h
  loc_00412D94: lea ecx, var_138
  loc_00412D9A: push ecx
  loc_00412D9B: lea edx, var_A0
  loc_00412DA1: push edx
  loc_00412DA2: mov eax, Me
  loc_00412DA5: mov ecx, [eax]
  loc_00412DA7: mov edx, Me
  loc_00412DAA: push edx
  loc_00412DAB: call [ecx+00000708h]
  loc_00412DB1: mov var_2C0, eax
  loc_00412DB7: cmp var_2C0, 00000000h
  loc_00412DBE: jge 00412DE3h
  loc_00412DC0: push 00000708h
  loc_00412DC5: push 0040579Ch ; "#]=VｫoyAｷ ;ﾑs：ﾚLabel12"
  loc_00412DCA: mov eax, Me
  loc_00412DCD: push eax
  loc_00412DCE: mov ecx, var_2C0
  loc_00412DD4: push ecx
  loc_00412DD5: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00412DDB: mov var_578, eax
  loc_00412DE1: jmp 00412DEDh
  loc_00412DE3: mov var_578, 00000000h
  loc_00412DED: lea ecx, var_138
  loc_00412DF3: call [00401020h] ; __vbaFreeVar
  loc_00412DF9: mov var_2BC, 00000000h
  loc_00412E03: mov var_2B8, 00000000h
  loc_00412E0D: mov var_2B4, 00000000h
  loc_00412E17: mov var_2B0, 00000000h
  loc_00412E21: mov var_2AC, 00000000h
  loc_00412E2B: mov var_2A8, 00000000h
  loc_00412E35: mov var_298, 00000000h
  loc_00412E3F: mov var_294, 00000000h
  loc_00412E49: mov edx, 00406B58h
  loc_00412E4E: lea ecx, var_C8
  loc_00412E54: call [00401178h] ; __vbaStrCopy
  loc_00412E5A: mov var_290, 00000000h
  loc_00412E64: mov var_28C, FFFFFFh
  loc_00412E6D: lea edx, var_2BC
  loc_00412E73: push edx
  loc_00412E74: lea eax, var_2B4
  loc_00412E7A: push eax
  loc_00412E7B: lea ecx, var_2AC
  loc_00412E81: push ecx
  loc_00412E82: lea edx, var_298
  loc_00412E88: push edx
  loc_00412E89: lea eax, var_294
  loc_00412E8F: push eax
  loc_00412E90: lea ecx, var_C8
  loc_00412E96: push ecx
  loc_00412E97: lea edx, var_290
  loc_00412E9D: push edx
  loc_00412E9E: lea eax, var_28C
  loc_00412EA4: push eax
  loc_00412EA5: lea ecx, var_138
  loc_00412EAB: push ecx
  loc_00412EAC: call 0041F410h
  loc_00412EB1: lea ecx, var_C8
  loc_00412EB7: call [004011F4h] ; __vbaFreeStr
  loc_00412EBD: lea ecx, var_138
  loc_00412EC3: call [00401020h] ; __vbaFreeVar
  loc_00412EC9: mov var_160, 80020004h
  loc_00412ED3: mov var_168, 0000000Ah
  loc_00412EDD: mov var_150, 80020004h
  loc_00412EE7: mov var_158, 0000000Ah
  loc_00412EF1: mov var_260, 004050E8h ; "IMT LampElectrical Probing"
  loc_00412EFB: mov var_268, 00000008h
  loc_00412F05: lea edx, var_268
  loc_00412F0B: lea ecx, var_148
  loc_00412F11: call [004011B4h] ; __vbaVarDup
  loc_00412F17: mov var_250, 00406D10h ; "Engineering Mode Done"
  loc_00412F21: mov var_258, 00000008h
  loc_00412F2B: lea edx, var_258
  loc_00412F31: lea ecx, var_138
  loc_00412F37: call [004011B4h] ; __vbaVarDup
  loc_00412F3D: lea edx, var_168
  loc_00412F43: push edx
  loc_00412F44: lea eax, var_158
  loc_00412F4A: push eax
  loc_00412F4B: lea ecx, var_148
  loc_00412F51: push ecx
  loc_00412F52: push 00000000h
  loc_00412F54: lea edx, var_138
  loc_00412F5A: push edx
  loc_00412F5B: call [00401084h] ; rtcMsgBox
  loc_00412F61: lea eax, var_168
  loc_00412F67: push eax
  loc_00412F68: lea ecx, var_158
  loc_00412F6E: push ecx
  loc_00412F6F: lea edx, var_148
  loc_00412F75: push edx
  loc_00412F76: lea eax, var_138
  loc_00412F7C: push eax
  loc_00412F7D: push 00000004h
  loc_00412F7F: call [00401038h] ; __vbaFreeVarList
  loc_00412F85: add esp, 00000014h
  loc_00412F88: mov ecx, Me
  loc_00412F8B: mov edx, [ecx]
  loc_00412F8D: mov eax, Me
  loc_00412F90: push eax
  loc_00412F91: call [edx+00000390h]
  loc_00412F97: push eax
  loc_00412F98: lea ecx, var_118
  loc_00412F9E: push ecx
  loc_00412F9F: call [00401080h] ; __vbaObjSet
  loc_00412FA5: mov var_2C0, eax
  loc_00412FAB: push 00406C50h ; "GO"
  loc_00412FB0: mov edx, var_2C0
  loc_00412FB6: mov eax, [edx]
  loc_00412FB8: mov ecx, var_2C0
  loc_00412FBE: push ecx
  loc_00412FBF: call [eax+00000054h]
  loc_00412FC2: fnclex
  loc_00412FC4: mov var_2C4, eax
  loc_00412FCA: cmp var_2C4, 00000000h
  loc_00412FD1: jge 00412FF6h
  loc_00412FD3: push 00000054h
  loc_00412FD5: push 00406128h
  loc_00412FDA: mov edx, var_2C0
  loc_00412FE0: push edx
  loc_00412FE1: mov eax, var_2C4
  loc_00412FE7: push eax
  loc_00412FE8: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00412FEE: mov var_57C, eax
  loc_00412FF4: jmp 00413000h
  loc_00412FF6: mov var_57C, 00000000h
  loc_00413000: lea ecx, var_118
  loc_00413006: call [004011F0h] ; __vbaFreeObj
  loc_0041300C: push 00405B8Ch
  loc_00413011: push 00000000h
  loc_00413013: call [004011D4h] ; __vbaCastObj
  loc_00413019: push eax
  loc_0041301A: lea ecx, var_C0
  loc_00413020: push ecx
  loc_00413021: call [00401080h] ; __vbaObjSet
  loc_00413027: jmp 0041489Fh
  loc_0041302C: mov var_31C, 00000004h
  loc_00413036: mov var_318, 00000001h
  loc_00413040: mov var_60, 00000001h
  loc_00413047: jmp 0041305Bh
  loc_00413049: mov edx, var_60
  loc_0041304C: add edx, var_318
  loc_00413052: jo 00414AAFh
  loc_00413058: mov var_60, edx
  loc_0041305B: mov eax, var_60
  loc_0041305E: cmp eax, var_31C
  loc_00413064: jg 00414892h
  loc_0041306A: cmp var_60, 00000001h
  loc_0041306E: jnz 00413896h
  loc_00413074: movsx ecx, [00423032h]
  loc_0041307B: test ecx, ecx
  loc_0041307D: jz 0041345Fh
  loc_00413083: mov edx, 00406A98h ; "Voltage"
  loc_00413088: lea ecx, var_C8
  loc_0041308E: call [00401178h] ; __vbaStrCopy
  loc_00413094: lea edx, var_CC
  loc_0041309A: push edx
  loc_0041309B: lea eax, var_C8
  loc_004130A1: push eax
  loc_004130A2: mov ecx, var_C0
  loc_004130A8: mov edx, [ecx]
  loc_004130AA: mov eax, var_C0
  loc_004130B0: push eax
  loc_004130B1: call [edx+0000002Ch]
  loc_004130B4: fnclex
  loc_004130B6: mov var_2C0, eax
  loc_004130BC: cmp var_2C0, 00000000h
  loc_004130C3: jge 004130E8h
  loc_004130C5: push 0000002Ch
  loc_004130C7: push 00405B8Ch
  loc_004130CC: mov ecx, var_C0
  loc_004130D2: push ecx
  loc_004130D3: mov edx, var_2C0
  loc_004130D9: push edx
  loc_004130DA: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004130E0: mov var_580, eax
  loc_004130E6: jmp 004130F2h
  loc_004130E8: mov var_580, 00000000h
  loc_004130F2: mov edx, 00406910h ; "Averages"
  loc_004130F7: lea ecx, var_D0
  loc_004130FD: call [00401178h] ; __vbaStrCopy
  loc_00413103: lea eax, var_D4
  loc_00413109: push eax
  loc_0041310A: lea ecx, var_D0
  loc_00413110: push ecx
  loc_00413111: mov edx, var_C0
  loc_00413117: mov eax, [edx]
  loc_00413119: mov ecx, var_C0
  loc_0041311F: push ecx
  loc_00413120: call [eax+0000002Ch]
  loc_00413123: fnclex
  loc_00413125: mov var_2C4, eax
  loc_0041312B: cmp var_2C4, 00000000h
  loc_00413132: jge 00413157h
  loc_00413134: push 0000002Ch
  loc_00413136: push 00405B8Ch
  loc_0041313B: mov edx, var_C0
  loc_00413141: push edx
  loc_00413142: mov eax, var_2C4
  loc_00413148: push eax
  loc_00413149: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041314F: mov var_584, eax
  loc_00413155: jmp 00413161h
  loc_00413157: mov var_584, 00000000h
  loc_00413161: mov edx, 004068A8h ; "MeterDelay"
  loc_00413166: lea ecx, var_D8
  loc_0041316C: call [00401178h] ; __vbaStrCopy
  loc_00413172: lea ecx, var_DC
  loc_00413178: push ecx
  loc_00413179: lea edx, var_D8
  loc_0041317F: push edx
  loc_00413180: mov eax, var_C0
  loc_00413186: mov ecx, [eax]
  loc_00413188: mov edx, var_C0
  loc_0041318E: push edx
  loc_0041318F: call [ecx+0000002Ch]
  loc_00413192: fnclex
  loc_00413194: mov var_2C8, eax
  loc_0041319A: cmp var_2C8, 00000000h
  loc_004131A1: jge 004131C6h
  loc_004131A3: push 0000002Ch
  loc_004131A5: push 00405B8Ch
  loc_004131AA: mov eax, var_C0
  loc_004131B0: push eax
  loc_004131B1: mov ecx, var_2C8
  loc_004131B7: push ecx
  loc_004131B8: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004131BE: mov var_588, eax
  loc_004131C4: jmp 004131D0h
  loc_004131C6: mov var_588, 00000000h
  loc_004131D0: mov edx, 004069F8h ; "NPLC"
  loc_004131D5: lea ecx, var_E0
  loc_004131DB: call [00401178h] ; __vbaStrCopy
  loc_004131E1: lea edx, var_E4
  loc_004131E7: push edx
  loc_004131E8: lea eax, var_E0
  loc_004131EE: push eax
  loc_004131EF: mov ecx, var_C0
  loc_004131F5: mov edx, [ecx]
  loc_004131F7: mov eax, var_C0
  loc_004131FD: push eax
  loc_004131FE: call [edx+0000002Ch]
  loc_00413201: fnclex
  loc_00413203: mov var_2CC, eax
  loc_00413209: cmp var_2CC, 00000000h
  loc_00413210: jge 00413235h
  loc_00413212: push 0000002Ch
  loc_00413214: push 00405B8Ch
  loc_00413219: mov ecx, var_C0
  loc_0041321F: push ecx
  loc_00413220: mov edx, var_2CC
  loc_00413226: push edx
  loc_00413227: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041322D: mov var_58C, eax
  loc_00413233: jmp 0041323Fh
  loc_00413235: mov var_58C, 00000000h
  loc_0041323F: mov edx, 00406764h ; "MeterCurrentLimit"
  loc_00413244: lea ecx, var_E8
  loc_0041324A: call [00401178h] ; __vbaStrCopy
  loc_00413250: lea eax, var_EC
  loc_00413256: push eax
  loc_00413257: lea ecx, var_E8
  loc_0041325D: push ecx
  loc_0041325E: mov edx, var_C0
  loc_00413264: mov eax, [edx]
  loc_00413266: mov ecx, var_C0
  loc_0041326C: push ecx
  loc_0041326D: call [eax+0000002Ch]
  loc_00413270: fnclex
  loc_00413272: mov var_2D0, eax
  loc_00413278: cmp var_2D0, 00000000h
  loc_0041327F: jge 004132A4h
  loc_00413281: push 0000002Ch
  loc_00413283: push 00405B8Ch
  loc_00413288: mov edx, var_C0
  loc_0041328E: push edx
  loc_0041328F: mov eax, var_2D0
  loc_00413295: push eax
  loc_00413296: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041329C: mov var_590, eax
  loc_004132A2: jmp 004132AEh
  loc_004132A4: mov var_590, 00000000h
  loc_004132AE: mov edx, 004060DCh ; "MeterRange"
  loc_004132B3: lea ecx, var_F0
  loc_004132B9: call [00401178h] ; __vbaStrCopy
  loc_004132BF: lea ecx, var_F4
  loc_004132C5: push ecx
  loc_004132C6: lea edx, var_F0
  loc_004132CC: push edx
  loc_004132CD: mov eax, var_C0
  loc_004132D3: mov ecx, [eax]
  loc_004132D5: mov edx, var_C0
  loc_004132DB: push edx
  loc_004132DC: call [ecx+0000002Ch]
  loc_004132DF: fnclex
  loc_004132E1: mov var_2D4, eax
  loc_004132E7: cmp var_2D4, 00000000h
  loc_004132EE: jge 00413313h
  loc_004132F0: push 0000002Ch
  loc_004132F2: push 00405B8Ch
  loc_004132F7: mov eax, var_C0
  loc_004132FD: push eax
  loc_004132FE: mov ecx, var_2D4
  loc_00413304: push ecx
  loc_00413305: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041330B: mov var_594, eax
  loc_00413311: jmp 0041331Dh
  loc_00413313: mov var_594, 00000000h
  loc_0041331D: mov edx, var_F4
  loc_00413323: mov var_364, edx
  loc_00413329: mov var_F4, 00000000h
  loc_00413333: mov edx, var_364
  loc_00413339: lea ecx, var_FC
  loc_0041333F: call [004011D0h] ; __vbaStrMove
  loc_00413345: mov eax, var_EC
  loc_0041334B: mov var_368, eax
  loc_00413351: mov var_EC, 00000000h
  loc_0041335B: mov edx, var_368
  loc_00413361: lea ecx, var_F8
  loc_00413367: call [004011D0h] ; __vbaStrMove
  loc_0041336D: mov ecx, var_E4
  loc_00413373: push ecx
  loc_00413374: call [0040117Ch] ; __vbaI4Str
  loc_0041337A: mov var_294, eax
  loc_00413380: mov edx, var_DC
  loc_00413386: push edx
  loc_00413387: call [00401160h] ; __vbaR8Str
  loc_0041338D: fstp real8 ptr var_2B4
  loc_00413393: mov eax, var_D4
  loc_00413399: push eax
  loc_0041339A: call [0040117Ch] ; __vbaI4Str
  loc_004133A0: mov var_290, eax
  loc_004133A6: mov ecx, var_CC
  loc_004133AC: push ecx
  loc_004133AD: call [00401160h] ; __vbaR8Str
  loc_004133B3: fstp real8 ptr var_2AC
  loc_004133B9: lea edx, var_FC
  loc_004133BF: push edx
  loc_004133C0: lea eax, var_F8
  loc_004133C6: push eax
  loc_004133C7: lea ecx, var_294
  loc_004133CD: push ecx
  loc_004133CE: lea edx, var_2B4
  loc_004133D4: push edx
  loc_004133D5: lea eax, var_290
  loc_004133DB: push eax
  loc_004133DC: lea ecx, var_2AC
  loc_004133E2: push ecx
  loc_004133E3: lea edx, var_138
  loc_004133E9: push edx
  loc_004133EA: call 004208F0h
  loc_004133EF: lea eax, var_FC
  loc_004133F5: push eax
  loc_004133F6: lea ecx, var_F8
  loc_004133FC: push ecx
  loc_004133FD: lea edx, var_F0
  loc_00413403: push edx
  loc_00413404: lea eax, var_E8
  loc_0041340A: push eax
  loc_0041340B: lea ecx, var_E4
  loc_00413411: push ecx
  loc_00413412: lea edx, var_E0
  loc_00413418: push edx
  loc_00413419: lea eax, var_DC
  loc_0041341F: push eax
  loc_00413420: lea ecx, var_D8
  loc_00413426: push ecx
  loc_00413427: lea edx, var_D4
  loc_0041342D: push edx
  loc_0041342E: lea eax, var_D0
  loc_00413434: push eax
  loc_00413435: lea ecx, var_CC
  loc_0041343B: push ecx
  loc_0041343C: lea edx, var_C8
  loc_00413442: push edx
  loc_00413443: push 0000000Ch
  loc_00413445: call [00401180h] ; __vbaFreeStrList
  loc_0041344B: add esp, 00000034h
  loc_0041344E: lea ecx, var_138
  loc_00413454: call [00401020h] ; __vbaFreeVar
  loc_0041345A: jmp 00413896h
  loc_0041345F: mov eax, Me
  loc_00413462: mov ecx, [eax]
  loc_00413464: mov edx, Me
  loc_00413467: push edx
  loc_00413468: call [ecx+00000324h]
  loc_0041346E: push eax
  loc_0041346F: lea eax, var_118
  loc_00413475: push eax
  loc_00413476: call [00401080h] ; __vbaObjSet
  loc_0041347C: mov var_2C0, eax
  loc_00413482: lea ecx, var_C8
  loc_00413488: push ecx
  loc_00413489: mov edx, var_2C0
  loc_0041348F: mov eax, [edx]
  loc_00413491: mov ecx, var_2C0
  loc_00413497: push ecx
  loc_00413498: call [eax+000000A8h]
  loc_0041349E: fnclex
  loc_004134A0: mov var_2C4, eax
  loc_004134A6: cmp var_2C4, 00000000h
  loc_004134AD: jge 004134D5h
  loc_004134AF: push 000000A8h
  loc_004134B4: push 004055DCh
  loc_004134B9: mov edx, var_2C0
  loc_004134BF: push edx
  loc_004134C0: mov eax, var_2C4
  loc_004134C6: push eax
  loc_004134C7: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004134CD: mov var_598, eax
  loc_004134D3: jmp 004134DFh
  loc_004134D5: mov var_598, 00000000h
  loc_004134DF: mov ecx, Me
  loc_004134E2: mov edx, [ecx]
  loc_004134E4: mov eax, Me
  loc_004134E7: push eax
  loc_004134E8: call [edx+00000310h]
  loc_004134EE: push eax
  loc_004134EF: lea ecx, var_11C
  loc_004134F5: push ecx
  loc_004134F6: call [00401080h] ; __vbaObjSet
  loc_004134FC: mov var_2C8, eax
  loc_00413502: lea edx, var_CC
  loc_00413508: push edx
  loc_00413509: mov eax, var_2C8
  loc_0041350F: mov ecx, [eax]
  loc_00413511: mov edx, var_2C8
  loc_00413517: push edx
  loc_00413518: call [ecx+000000A0h]
  loc_0041351E: fnclex
  loc_00413520: mov var_2CC, eax
  loc_00413526: cmp var_2CC, 00000000h
  loc_0041352D: jge 00413555h
  loc_0041352F: push 000000A0h
  loc_00413534: push 00405398h
  loc_00413539: mov eax, var_2C8
  loc_0041353F: push eax
  loc_00413540: mov ecx, var_2CC
  loc_00413546: push ecx
  loc_00413547: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041354D: mov var_59C, eax
  loc_00413553: jmp 0041355Fh
  loc_00413555: mov var_59C, 00000000h
  loc_0041355F: mov edx, Me
  loc_00413562: mov eax, [edx]
  loc_00413564: mov ecx, Me
  loc_00413567: push ecx
  loc_00413568: call [eax+00000314h]
  loc_0041356E: push eax
  loc_0041356F: lea edx, var_120
  loc_00413575: push edx
  loc_00413576: call [00401080h] ; __vbaObjSet
  loc_0041357C: mov var_2D0, eax
  loc_00413582: lea eax, var_D0
  loc_00413588: push eax
  loc_00413589: mov ecx, var_2D0
  loc_0041358F: mov edx, [ecx]
  loc_00413591: mov eax, var_2D0
  loc_00413597: push eax
  loc_00413598: call [edx+000000A0h]
  loc_0041359E: fnclex
  loc_004135A0: mov var_2D4, eax
  loc_004135A6: cmp var_2D4, 00000000h
  loc_004135AD: jge 004135D5h
  loc_004135AF: push 000000A0h
  loc_004135B4: push 00405398h
  loc_004135B9: mov ecx, var_2D0
  loc_004135BF: push ecx
  loc_004135C0: mov edx, var_2D4
  loc_004135C6: push edx
  loc_004135C7: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004135CD: mov var_5A0, eax
  loc_004135D3: jmp 004135DFh
  loc_004135D5: mov var_5A0, 00000000h
  loc_004135DF: mov edx, 004069F8h ; "NPLC"
  loc_004135E4: lea ecx, var_D4
  loc_004135EA: call [00401178h] ; __vbaStrCopy
  loc_004135F0: lea eax, var_D8
  loc_004135F6: push eax
  loc_004135F7: lea ecx, var_D4
  loc_004135FD: push ecx
  loc_004135FE: mov edx, var_C0
  loc_00413604: mov eax, [edx]
  loc_00413606: mov ecx, var_C0
  loc_0041360C: push ecx
  loc_0041360D: call [eax+0000002Ch]
  loc_00413610: fnclex
  loc_00413612: mov var_2D8, eax
  loc_00413618: cmp var_2D8, 00000000h
  loc_0041361F: jge 00413644h
  loc_00413621: push 0000002Ch
  loc_00413623: push 00405B8Ch
  loc_00413628: mov edx, var_C0
  loc_0041362E: push edx
  loc_0041362F: mov eax, var_2D8
  loc_00413635: push eax
  loc_00413636: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041363C: mov var_5A4, eax
  loc_00413642: jmp 0041364Eh
  loc_00413644: mov var_5A4, 00000000h
  loc_0041364E: mov ecx, Me
  loc_00413651: mov edx, [ecx]
  loc_00413653: mov eax, Me
  loc_00413656: push eax
  loc_00413657: call [edx+00000304h]
  loc_0041365D: push eax
  loc_0041365E: lea ecx, var_124
  loc_00413664: push ecx
  loc_00413665: call [00401080h] ; __vbaObjSet
  loc_0041366B: mov var_2DC, eax
  loc_00413671: lea edx, var_DC
  loc_00413677: push edx
  loc_00413678: mov eax, var_2DC
  loc_0041367E: mov ecx, [eax]
  loc_00413680: mov edx, var_2DC
  loc_00413686: push edx
  loc_00413687: call [ecx+000000A0h]
  loc_0041368D: fnclex
  loc_0041368F: mov var_2E0, eax
  loc_00413695: cmp var_2E0, 00000000h
  loc_0041369C: jge 004136C4h
  loc_0041369E: push 000000A0h
  loc_004136A3: push 00405398h
  loc_004136A8: mov eax, var_2DC
  loc_004136AE: push eax
  loc_004136AF: mov ecx, var_2E0
  loc_004136B5: push ecx
  loc_004136B6: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004136BC: mov var_5A8, eax
  loc_004136C2: jmp 004136CEh
  loc_004136C4: mov var_5A8, 00000000h
  loc_004136CE: mov edx, Me
  loc_004136D1: mov eax, [edx]
  loc_004136D3: mov ecx, Me
  loc_004136D6: push ecx
  loc_004136D7: call [eax+00000308h]
  loc_004136DD: push eax
  loc_004136DE: lea edx, var_128
  loc_004136E4: push edx
  loc_004136E5: call [00401080h] ; __vbaObjSet
  loc_004136EB: mov var_2E4, eax
  loc_004136F1: lea eax, var_E0
  loc_004136F7: push eax
  loc_004136F8: mov ecx, var_2E4
  loc_004136FE: mov edx, [ecx]
  loc_00413700: mov eax, var_2E4
  loc_00413706: push eax
  loc_00413707: call [edx+000000A0h]
  loc_0041370D: fnclex
  loc_0041370F: mov var_2E8, eax
  loc_00413715: cmp var_2E8, 00000000h
  loc_0041371C: jge 00413744h
  loc_0041371E: push 000000A0h
  loc_00413723: push 00405398h
  loc_00413728: mov ecx, var_2E4
  loc_0041372E: push ecx
  loc_0041372F: mov edx, var_2E8
  loc_00413735: push edx
  loc_00413736: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041373C: mov var_5AC, eax
  loc_00413742: jmp 0041374Eh
  loc_00413744: mov var_5AC, 00000000h
  loc_0041374E: mov eax, var_E0
  loc_00413754: mov var_36C, eax
  loc_0041375A: mov var_E0, 00000000h
  loc_00413764: mov edx, var_36C
  loc_0041376A: lea ecx, var_E8
  loc_00413770: call [004011D0h] ; __vbaStrMove
  loc_00413776: mov ecx, var_DC
  loc_0041377C: mov var_370, ecx
  loc_00413782: mov var_DC, 00000000h
  loc_0041378C: mov edx, var_370
  loc_00413792: lea ecx, var_E4
  loc_00413798: call [004011D0h] ; __vbaStrMove
  loc_0041379E: mov edx, var_D8
  loc_004137A4: push edx
  loc_004137A5: call [0040117Ch] ; __vbaI4Str
  loc_004137AB: mov var_294, eax
  loc_004137B1: mov eax, var_D0
  loc_004137B7: push eax
  loc_004137B8: call [00401160h] ; __vbaR8Str
  loc_004137BE: fstp real8 ptr var_2B4
  loc_004137C4: mov ecx, var_CC
  loc_004137CA: push ecx
  loc_004137CB: call [0040117Ch] ; __vbaI4Str
  loc_004137D1: mov var_290, eax
  loc_004137D7: mov edx, var_C8
  loc_004137DD: push edx
  loc_004137DE: call [00401160h] ; __vbaR8Str
  loc_004137E4: fstp real8 ptr var_2AC
  loc_004137EA: lea eax, var_E8
  loc_004137F0: push eax
  loc_004137F1: lea ecx, var_E4
  loc_004137F7: push ecx
  loc_004137F8: lea edx, var_294
  loc_004137FE: push edx
  loc_004137FF: lea eax, var_2B4
  loc_00413805: push eax
  loc_00413806: lea ecx, var_290
  loc_0041380C: push ecx
  loc_0041380D: lea edx, var_2AC
  loc_00413813: push edx
  loc_00413814: lea eax, var_138
  loc_0041381A: push eax
  loc_0041381B: call 004208F0h
  loc_00413820: lea ecx, var_E8
  loc_00413826: push ecx
  loc_00413827: lea edx, var_E4
  loc_0041382D: push edx
  loc_0041382E: lea eax, var_D8
  loc_00413834: push eax
  loc_00413835: lea ecx, var_D4
  loc_0041383B: push ecx
  loc_0041383C: lea edx, var_D0
  loc_00413842: push edx
  loc_00413843: lea eax, var_CC
  loc_00413849: push eax
  loc_0041384A: lea ecx, var_C8
  loc_00413850: push ecx
  loc_00413851: push 00000007h
  loc_00413853: call [00401180h] ; __vbaFreeStrList
  loc_00413859: add esp, 00000020h
  loc_0041385C: lea edx, var_128
  loc_00413862: push edx
  loc_00413863: lea eax, var_124
  loc_00413869: push eax
  loc_0041386A: lea ecx, var_120
  loc_00413870: push ecx
  loc_00413871: lea edx, var_11C
  loc_00413877: push edx
  loc_00413878: lea eax, var_118
  loc_0041387E: push eax
  loc_0041387F: push 00000005h
  loc_00413881: call [00401040h] ; __vbaFreeObjList
  loc_00413887: add esp, 00000018h
  loc_0041388A: lea ecx, var_138
  loc_00413890: call [00401020h] ; __vbaFreeVar
  loc_00413896: mov ecx, var_74
  loc_00413899: mov var_324, ecx
  loc_0041389F: mov var_320, 00000001h
  loc_004138A9: mov var_64, 00000001h
  loc_004138B0: jmp 004138C4h
  loc_004138B2: mov edx, var_64
  loc_004138B5: add edx, var_320
  loc_004138BB: jo 00414AAFh
  loc_004138C1: mov var_64, edx
  loc_004138C4: mov eax, var_64
  loc_004138C7: cmp eax, var_324
  loc_004138CD: jg 0041488Dh
  loc_004138D3: cmp var_64, 00000001h
  loc_004138D7: jnz 004138E4h
  loc_004138D9: mov var_9C, FFFFFFh
  loc_004138E2: jmp 004138EDh
  loc_004138E4: mov var_9C, 0000h
  loc_004138ED: mov ecx, var_64
  loc_004138F0: cmp ecx, var_74
  loc_004138F3: jnz 004138FDh
  loc_004138F5: mov var_70, FFFFFFh
  loc_004138FB: jmp 00413903h
  loc_004138FD: mov var_70, 0000h
  loc_00413903: mov edx, 00406AC0h ; "Delay2"
  loc_00413908: lea ecx, var_C8
  loc_0041390E: call [00401178h] ; __vbaStrCopy
  loc_00413914: lea edx, var_CC
  loc_0041391A: push edx
  loc_0041391B: lea eax, var_C8
  loc_00413921: push eax
  loc_00413922: mov ecx, var_C0
  loc_00413928: mov edx, [ecx]
  loc_0041392A: mov eax, var_C0
  loc_00413930: push eax
  loc_00413931: call [edx+0000002Ch]
  loc_00413934: fnclex
  loc_00413936: mov var_2C8, eax
  loc_0041393C: cmp var_2C8, 00000000h
  loc_00413943: jge 00413968h
  loc_00413945: push 0000002Ch
  loc_00413947: push 00405B8Ch
  loc_0041394C: mov ecx, var_C0
  loc_00413952: push ecx
  loc_00413953: mov edx, var_2C8
  loc_00413959: push edx
  loc_0041395A: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00413960: mov var_5B0, eax
  loc_00413966: jmp 00413972h
  loc_00413968: mov var_5B0, 00000000h
  loc_00413972: mov eax, var_CC
  loc_00413978: push eax
  loc_00413979: call [0040117Ch] ; __vbaI4Str
  loc_0041397F: mov var_290, eax
  loc_00413985: mov ecx, var_60
  loc_00413988: sub ecx, 00000001h
  loc_0041398B: mov var_2C4, ecx
  loc_00413991: cmp var_2C4, 00000004h
  loc_00413998: jae 004139A6h
  loc_0041399A: mov var_5B4, 00000000h
  loc_004139A4: jmp 004139B2h
  loc_004139A6: call [004010D8h] ; __vbaGenerateBoundsError
  loc_004139AC: mov var_5B4, eax
  loc_004139B2: mov edx, var_60
  loc_004139B5: sub edx, 00000001h
  loc_004139B8: mov var_2C0, edx
  loc_004139BE: cmp var_2C0, 00000004h
  loc_004139C5: jae 004139D3h
  loc_004139C7: mov var_5B8, 00000000h
  loc_004139D1: jmp 004139DFh
  loc_004139D3: call [004010D8h] ; __vbaGenerateBoundsError
  loc_004139D9: mov var_5B8, eax
  loc_004139DF: lea eax, var_290
  loc_004139E5: push eax
  loc_004139E6: lea ecx, var_70
  loc_004139E9: push ecx
  loc_004139EA: lea edx, var_9C
  loc_004139F0: push edx
  loc_004139F1: mov eax, var_2C4
  loc_004139F7: mov ecx, var_2C
  loc_004139FA: lea edx, [ecx+eax*8]
  loc_004139FD: push edx
  loc_004139FE: mov eax, var_2C0
  loc_00413A04: mov ecx, var_AC
  loc_00413A0A: lea edx, [ecx+eax*8]
  loc_00413A0D: push edx
  loc_00413A0E: lea eax, var_60
  loc_00413A11: push eax
  loc_00413A12: call 0041FF90h
  loc_00413A17: lea ecx, var_CC
  loc_00413A1D: push ecx
  loc_00413A1E: lea edx, var_C8
  loc_00413A24: push edx
  loc_00413A25: push 00000002h
  loc_00413A27: call [00401180h] ; __vbaFreeStrList
  loc_00413A2D: add esp, 0000000Ch
  loc_00413A30: movsx eax, [00423032h]
  loc_00413A37: test eax, eax
  loc_00413A39: jz 00413EE9h
  loc_00413A3F: mov edx, 00406A98h ; "Voltage"
  loc_00413A44: lea ecx, var_C8
  loc_00413A4A: call [00401178h] ; __vbaStrCopy
  loc_00413A50: lea ecx, var_CC
  loc_00413A56: push ecx
  loc_00413A57: lea edx, var_C8
  loc_00413A5D: push edx
  loc_00413A5E: mov eax, var_C0
  loc_00413A64: mov ecx, [eax]
  loc_00413A66: mov edx, var_C0
  loc_00413A6C: push edx
  loc_00413A6D: call [ecx+0000002Ch]
  loc_00413A70: fnclex
  loc_00413A72: mov var_2C0, eax
  loc_00413A78: cmp var_2C0, 00000000h
  loc_00413A7F: jge 00413AA4h
  loc_00413A81: push 0000002Ch
  loc_00413A83: push 00405B8Ch
  loc_00413A88: mov eax, var_C0
  loc_00413A8E: push eax
  loc_00413A8F: mov ecx, var_2C0
  loc_00413A95: push ecx
  loc_00413A96: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00413A9C: mov var_5BC, eax
  loc_00413AA2: jmp 00413AAEh
  loc_00413AA4: mov var_5BC, 00000000h
  loc_00413AAE: mov edx, var_60
  loc_00413AB1: sub edx, 00000001h
  loc_00413AB4: mov var_2C8, edx
  loc_00413ABA: cmp var_2C8, 00000004h
  loc_00413AC1: jae 00413ACFh
  loc_00413AC3: mov var_5C0, 00000000h
  loc_00413ACD: jmp 00413ADBh
  loc_00413ACF: call [004010D8h] ; __vbaGenerateBoundsError
  loc_00413AD5: mov var_5C0, eax
  loc_00413ADB: mov eax, var_60
  loc_00413ADE: sub eax, 00000001h
  loc_00413AE1: mov var_2C4, eax
  loc_00413AE7: cmp var_2C4, 00000004h
  loc_00413AEE: jae 00413AFCh
  loc_00413AF0: mov var_5C4, 00000000h
  loc_00413AFA: jmp 00413B08h
  loc_00413AFC: call [004010D8h] ; __vbaGenerateBoundsError
  loc_00413B02: mov var_5C4, eax
  loc_00413B08: mov ecx, var_CC
  loc_00413B0E: push ecx
  loc_00413B0F: call [00401160h] ; __vbaR8Str
  loc_00413B15: fstp real8 ptr var_2AC
  loc_00413B1B: mov var_28C, 0000h
  loc_00413B24: mov edx, var_2C8
  loc_00413B2A: mov eax, var_2C
  loc_00413B2D: lea ecx, [eax+edx*8]
  loc_00413B30: push ecx
  loc_00413B31: mov edx, var_2C4
  loc_00413B37: mov eax, var_AC
  loc_00413B3D: lea ecx, [eax+edx*8]
  loc_00413B40: push ecx
  loc_00413B41: lea edx, var_2AC
  loc_00413B47: push edx
  loc_00413B48: lea eax, var_64
  loc_00413B4B: push eax
  loc_00413B4C: lea ecx, var_60
  loc_00413B4F: push ecx
  loc_00413B50: lea edx, var_40
  loc_00413B53: push edx
  loc_00413B54: lea eax, var_A0
  loc_00413B5A: push eax
  loc_00413B5B: lea ecx, var_28C
  loc_00413B61: push ecx
  loc_00413B62: lea edx, var_138
  loc_00413B68: push edx
  loc_00413B69: call 0041F410h
  loc_00413B6E: lea eax, var_CC
  loc_00413B74: push eax
  loc_00413B75: lea ecx, var_C8
  loc_00413B7B: push ecx
  loc_00413B7C: push 00000002h
  loc_00413B7E: call [00401180h] ; __vbaFreeStrList
  loc_00413B84: add esp, 0000000Ch
  loc_00413B87: lea ecx, var_138
  loc_00413B8D: call [00401020h] ; __vbaFreeVar
  loc_00413B93: mov edx, var_60
  loc_00413B96: push edx
  loc_00413B97: call [00401018h] ; __vbaStrI4
  loc_00413B9D: mov var_130, eax
  loc_00413BA3: mov var_138, 00000008h
  loc_00413BAD: lea eax, var_138
  loc_00413BB3: push eax
  loc_00413BB4: lea ecx, var_148
  loc_00413BBA: push ecx
  loc_00413BBB: call [004010A4h] ; rtcTrimVar
  loc_00413BC1: mov edx, var_64
  loc_00413BC4: push edx
  loc_00413BC5: call [00401018h] ; __vbaStrI4
  loc_00413BCB: mov var_180, eax
  loc_00413BD1: mov var_188, 00000008h
  loc_00413BDB: lea eax, var_188
  loc_00413BE1: push eax
  loc_00413BE2: lea ecx, var_198
  loc_00413BE8: push ecx
  loc_00413BE9: call [004010A4h] ; rtcTrimVar
  loc_00413BEF: mov edx, var_60
  loc_00413BF2: sub edx, 00000001h
  loc_00413BF5: mov var_2C0, edx
  loc_00413BFB: cmp var_2C0, 00000004h
  loc_00413C02: jae 00413C10h
  loc_00413C04: mov var_5C8, 00000000h
  loc_00413C0E: jmp 00413C1Ch
  loc_00413C10: call [004010D8h] ; __vbaGenerateBoundsError
  loc_00413C16: mov var_5C8, eax
  loc_00413C1C: mov eax, var_2C0
  loc_00413C22: mov ecx, var_2C
  loc_00413C25: mov edx, [ecx+eax*8+00000004h]
  loc_00413C29: push edx
  loc_00413C2A: mov eax, [ecx+eax*8]
  loc_00413C2D: push eax
  loc_00413C2E: call [00401104h] ; __vbaStrR8
  loc_00413C34: mov var_1C0, eax
  loc_00413C3A: mov var_1C8, 00000008h
  loc_00413C44: lea ecx, var_1C8
  loc_00413C4A: push ecx
  loc_00413C4B: lea edx, var_1D8
  loc_00413C51: push edx
  loc_00413C52: call [004010A4h] ; rtcTrimVar
  loc_00413C58: mov eax, var_60
  loc_00413C5B: sub eax, 00000001h
  loc_00413C5E: mov var_2C4, eax
  loc_00413C64: cmp var_2C4, 00000004h
  loc_00413C6B: jae 00413C79h
  loc_00413C6D: mov var_5CC, 00000000h
  loc_00413C77: jmp 00413C85h
  loc_00413C79: call [004010D8h] ; __vbaGenerateBoundsError
  loc_00413C7F: mov var_5CC, eax
  loc_00413C85: mov ecx, var_2C4
  loc_00413C8B: mov edx, var_AC
  loc_00413C91: mov eax, [edx+ecx*8+00000004h]
  loc_00413C95: push eax
  loc_00413C96: mov ecx, [edx+ecx*8]
  loc_00413C99: push ecx
  loc_00413C9A: call [00401104h] ; __vbaStrR8
  loc_00413CA0: mov var_200, eax
  loc_00413CA6: mov var_208, 00000008h
  loc_00413CB0: lea edx, var_208
  loc_00413CB6: push edx
  loc_00413CB7: lea eax, var_218
  loc_00413CBD: push eax
  loc_00413CBE: call [004010A4h] ; rtcTrimVar
  loc_00413CC4: mov ecx, var_40
  loc_00413CC7: push ecx
  loc_00413CC8: push 00406D40h
  loc_00413CCD: call [00401050h] ; __vbaStrCat
  loc_00413CD3: mov var_150, eax
  loc_00413CD9: mov var_158, 00000008h
  loc_00413CE3: mov var_250, 00406D40h
  loc_00413CED: mov var_258, 00000008h
  loc_00413CF7: mov var_260, 00406D40h
  loc_00413D01: mov var_268, 00000008h
  loc_00413D0B: mov var_270, 00406D40h
  loc_00413D15: mov var_278, 00000008h
  loc_00413D1F: mov var_280, 00406D40h
  loc_00413D29: mov var_288, 00000008h
  loc_00413D33: lea edx, var_158
  loc_00413D39: push edx
  loc_00413D3A: lea eax, var_148
  loc_00413D40: push eax
  loc_00413D41: lea ecx, var_168
  loc_00413D47: push ecx
  loc_00413D48: call [004011ACh] ; __vbaVarAdd
  loc_00413D4E: push eax
  loc_00413D4F: lea edx, var_258
  loc_00413D55: push edx
  loc_00413D56: lea eax, var_178
  loc_00413D5C: push eax
  loc_00413D5D: call [004011ACh] ; __vbaVarAdd
  loc_00413D63: push eax
  loc_00413D64: lea ecx, var_198
  loc_00413D6A: push ecx
  loc_00413D6B: lea edx, var_1A8
  loc_00413D71: push edx
  loc_00413D72: call [004011ACh] ; __vbaVarAdd
  loc_00413D78: push eax
  loc_00413D79: lea eax, var_268
  loc_00413D7F: push eax
  loc_00413D80: lea ecx, var_1B8
  loc_00413D86: push ecx
  loc_00413D87: call [004011ACh] ; __vbaVarAdd
  loc_00413D8D: push eax
  loc_00413D8E: lea edx, var_1D8
  loc_00413D94: push edx
  loc_00413D95: lea eax, var_1E8
  loc_00413D9B: push eax
  loc_00413D9C: call [004011ACh] ; __vbaVarAdd
  loc_00413DA2: push eax
  loc_00413DA3: lea ecx, var_278
  loc_00413DA9: push ecx
  loc_00413DAA: lea edx, var_1F8
  loc_00413DB0: push edx
  loc_00413DB1: call [004011ACh] ; __vbaVarAdd
  loc_00413DB7: push eax
  loc_00413DB8: lea eax, var_218
  loc_00413DBE: push eax
  loc_00413DBF: lea ecx, var_228
  loc_00413DC5: push ecx
  loc_00413DC6: call [004011ACh] ; __vbaVarAdd
  loc_00413DCC: push eax
  loc_00413DCD: lea edx, var_288
  loc_00413DD3: push edx
  loc_00413DD4: lea eax, var_238
  loc_00413DDA: push eax
  loc_00413DDB: call [004011ACh] ; __vbaVarAdd
  loc_00413DE1: push eax
  loc_00413DE2: call [00401030h] ; __vbaStrVarMove
  loc_00413DE8: mov edx, eax
  loc_00413DEA: lea ecx, var_C8
  loc_00413DF0: call [004011D0h] ; __vbaStrMove
  loc_00413DF6: lea ecx, var_248
  loc_00413DFC: push ecx
  loc_00413DFD: lea edx, var_C8
  loc_00413E03: push edx
  loc_00413E04: mov eax, Me
  loc_00413E07: mov ecx, [eax]
  loc_00413E09: mov edx, Me
  loc_00413E0C: push edx
  loc_00413E0D: call [ecx+00000700h]
  loc_00413E13: mov var_2C8, eax
  loc_00413E19: cmp var_2C8, 00000000h
  loc_00413E20: jge 00413E45h
  loc_00413E22: push 00000700h
  loc_00413E27: push 0040579Ch ; "#]=VｫoyAｷ ;ﾑs：ﾚLabel12"
  loc_00413E2C: mov eax, Me
  loc_00413E2F: push eax
  loc_00413E30: mov ecx, var_2C8
  loc_00413E36: push ecx
  loc_00413E37: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00413E3D: mov var_5D0, eax
  loc_00413E43: jmp 00413E4Fh
  loc_00413E45: mov var_5D0, 00000000h
  loc_00413E4F: lea ecx, var_C8
  loc_00413E55: call [004011F4h] ; __vbaFreeStr
  loc_00413E5B: lea edx, var_248
  loc_00413E61: push edx
  loc_00413E62: lea eax, var_238
  loc_00413E68: push eax
  loc_00413E69: lea ecx, var_228
  loc_00413E6F: push ecx
  loc_00413E70: lea edx, var_218
  loc_00413E76: push edx
  loc_00413E77: lea eax, var_1F8
  loc_00413E7D: push eax
  loc_00413E7E: lea ecx, var_208
  loc_00413E84: push ecx
  loc_00413E85: lea edx, var_1E8
  loc_00413E8B: push edx
  loc_00413E8C: lea eax, var_1D8
  loc_00413E92: push eax
  loc_00413E93: lea ecx, var_1B8
  loc_00413E99: push ecx
  loc_00413E9A: lea edx, var_1C8
  loc_00413EA0: push edx
  loc_00413EA1: lea eax, var_1A8
  loc_00413EA7: push eax
  loc_00413EA8: lea ecx, var_198
  loc_00413EAE: push ecx
  loc_00413EAF: lea edx, var_178
  loc_00413EB5: push edx
  loc_00413EB6: lea eax, var_188
  loc_00413EBC: push eax
  loc_00413EBD: lea ecx, var_168
  loc_00413EC3: push ecx
  loc_00413EC4: lea edx, var_148
  loc_00413ECA: push edx
  loc_00413ECB: lea eax, var_158
  loc_00413ED1: push eax
  loc_00413ED2: lea ecx, var_138
  loc_00413ED8: push ecx
  loc_00413ED9: push 00000012h
  loc_00413EDB: call [00401038h] ; __vbaFreeVarList
  loc_00413EE1: add esp, 0000004Ch
  loc_00413EE4: jmp 00414888h
  loc_00413EE9: movsx edx, var_9C
  loc_00413EF0: test edx, edx
  loc_00413EF2: jz 00413F3Ah
  loc_00413EF4: mov edx, 00406D48h ; "Die; Voltage; Iteration; Switch; Current; Voltage"
  loc_00413EF9: lea ecx, var_C8
  loc_00413EFF: call [00401178h] ; __vbaStrCopy
  loc_00413F05: lea eax, var_138
  loc_00413F0B: push eax
  loc_00413F0C: lea ecx, var_C8
  loc_00413F12: push ecx
  loc_00413F13: mov edx, Me
  loc_00413F16: mov eax, [edx]
  loc_00413F18: mov ecx, Me
  loc_00413F1B: push ecx
  loc_00413F1C: call [eax+0000072Ch]
  loc_00413F22: lea ecx, var_C8
  loc_00413F28: call [004011F4h] ; __vbaFreeStr
  loc_00413F2E: lea ecx, var_138
  loc_00413F34: call [00401020h] ; __vbaFreeVar
  loc_00413F3A: mov edx, Me
  loc_00413F3D: mov eax, [edx]
  loc_00413F3F: mov ecx, Me
  loc_00413F42: push ecx
  loc_00413F43: call [eax+00000370h]
  loc_00413F49: push eax
  loc_00413F4A: lea edx, var_118
  loc_00413F50: push edx
  loc_00413F51: call [00401080h] ; __vbaObjSet
  loc_00413F57: mov var_2C0, eax
  loc_00413F5D: lea eax, var_C8
  loc_00413F63: push eax
  loc_00413F64: mov ecx, var_2C0
  loc_00413F6A: mov edx, [ecx]
  loc_00413F6C: mov eax, var_2C0
  loc_00413F72: push eax
  loc_00413F73: call [edx+000000A8h]
  loc_00413F79: fnclex
  loc_00413F7B: mov var_2C4, eax
  loc_00413F81: cmp var_2C4, 00000000h
  loc_00413F88: jge 00413FB0h
  loc_00413F8A: push 000000A8h
  loc_00413F8F: push 004055DCh
  loc_00413F94: mov ecx, var_2C0
  loc_00413F9A: push ecx
  loc_00413F9B: mov edx, var_2C4
  loc_00413FA1: push edx
  loc_00413FA2: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00413FA8: mov var_5D4, eax
  loc_00413FAE: jmp 00413FBAh
  loc_00413FB0: mov var_5D4, 00000000h
  loc_00413FBA: mov eax, Me
  loc_00413FBD: mov ecx, [eax]
  loc_00413FBF: mov edx, Me
  loc_00413FC2: push edx
  loc_00413FC3: call [ecx+00000324h]
  loc_00413FC9: push eax
  loc_00413FCA: lea eax, var_11C
  loc_00413FD0: push eax
  loc_00413FD1: call [00401080h] ; __vbaObjSet
  loc_00413FD7: mov var_2C8, eax
  loc_00413FDD: lea ecx, var_CC
  loc_00413FE3: push ecx
  loc_00413FE4: mov edx, var_2C8
  loc_00413FEA: mov eax, [edx]
  loc_00413FEC: mov ecx, var_2C8
  loc_00413FF2: push ecx
  loc_00413FF3: call [eax+000000A8h]
  loc_00413FF9: fnclex
  loc_00413FFB: mov var_2CC, eax
  loc_00414001: cmp var_2CC, 00000000h
  loc_00414008: jge 00414030h
  loc_0041400A: push 000000A8h
  loc_0041400F: push 004055DCh
  loc_00414014: mov edx, var_2C8
  loc_0041401A: push edx
  loc_0041401B: mov eax, var_2CC
  loc_00414021: push eax
  loc_00414022: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00414028: mov var_5D8, eax
  loc_0041402E: jmp 0041403Ah
  loc_00414030: mov var_5D8, 00000000h
  loc_0041403A: mov ecx, var_64
  loc_0041403D: push ecx
  loc_0041403E: call [00401018h] ; __vbaStrI4
  loc_00414044: mov var_130, eax
  loc_0041404A: mov var_138, 00000008h
  loc_00414054: lea edx, var_138
  loc_0041405A: push edx
  loc_0041405B: lea eax, var_148
  loc_00414061: push eax
  loc_00414062: call [004010A4h] ; rtcTrimVar
  loc_00414068: mov ecx, var_60
  loc_0041406B: push ecx
  loc_0041406C: call [00401018h] ; __vbaStrI4
  loc_00414072: mov var_180, eax
  loc_00414078: mov var_188, 00000008h
  loc_00414082: lea edx, var_188
  loc_00414088: push edx
  loc_00414089: lea eax, var_198
  loc_0041408F: push eax
  loc_00414090: call [004010A4h] ; rtcTrimVar
  loc_00414096: mov ecx, var_60
  loc_00414099: sub ecx, 00000001h
  loc_0041409C: mov var_2D0, ecx
  loc_004140A2: cmp var_2D0, 00000004h
  loc_004140A9: jae 004140B7h
  loc_004140AB: mov var_5DC, 00000000h
  loc_004140B5: jmp 004140C3h
  loc_004140B7: call [004010D8h] ; __vbaGenerateBoundsError
  loc_004140BD: mov var_5DC, eax
  loc_004140C3: mov edx, var_2D0
  loc_004140C9: mov eax, var_2C
  loc_004140CC: mov ecx, [eax+edx*8+00000004h]
  loc_004140D0: push ecx
  loc_004140D1: mov edx, [eax+edx*8]
  loc_004140D4: push edx
  loc_004140D5: call [00401104h] ; __vbaStrR8
  loc_004140DB: mov var_1C0, eax
  loc_004140E1: mov var_1C8, 00000008h
  loc_004140EB: lea eax, var_1C8
  loc_004140F1: push eax
  loc_004140F2: lea ecx, var_1D8
  loc_004140F8: push ecx
  loc_004140F9: call [004010A4h] ; rtcTrimVar
  loc_004140FF: mov edx, var_60
  loc_00414102: sub edx, 00000001h
  loc_00414105: mov var_2D4, edx
  loc_0041410B: cmp var_2D4, 00000004h
  loc_00414112: jae 00414120h
  loc_00414114: mov var_5E0, 00000000h
  loc_0041411E: jmp 0041412Ch
  loc_00414120: call [004010D8h] ; __vbaGenerateBoundsError
  loc_00414126: mov var_5E0, eax
  loc_0041412C: mov eax, var_2D4
  loc_00414132: mov ecx, var_AC
  loc_00414138: mov edx, [ecx+eax*8+00000004h]
  loc_0041413C: push edx
  loc_0041413D: mov eax, [ecx+eax*8]
  loc_00414140: push eax
  loc_00414141: call [00401104h] ; __vbaStrR8
  loc_00414147: mov var_200, eax
  loc_0041414D: mov var_208, 00000008h
  loc_00414157: lea ecx, var_208
  loc_0041415D: push ecx
  loc_0041415E: lea edx, var_218
  loc_00414164: push edx
  loc_00414165: call [004010A4h] ; rtcTrimVar
  loc_0041416B: mov eax, var_C8
  loc_00414171: push eax
  loc_00414172: push 00406D40h
  loc_00414177: call [00401050h] ; __vbaStrCat
  loc_0041417D: mov edx, eax
  loc_0041417F: lea ecx, var_D0
  loc_00414185: call [004011D0h] ; __vbaStrMove
  loc_0041418B: push eax
  loc_0041418C: mov ecx, var_CC
  loc_00414192: push ecx
  loc_00414193: call [00401050h] ; __vbaStrCat
  loc_00414199: mov edx, eax
  loc_0041419B: lea ecx, var_D4
  loc_004141A1: call [004011D0h] ; __vbaStrMove
  loc_004141A7: push eax
  loc_004141A8: push 00406D40h
  loc_004141AD: call [00401050h] ; __vbaStrCat
  loc_004141B3: mov var_150, eax
  loc_004141B9: mov var_158, 00000008h
  loc_004141C3: mov var_250, 00406D40h
  loc_004141CD: mov var_258, 00000008h
  loc_004141D7: mov var_260, 00406D40h
  loc_004141E1: mov var_268, 00000008h
  loc_004141EB: mov var_270, 00406D40h
  loc_004141F5: mov var_278, 00000008h
  loc_004141FF: mov var_280, 00406D40h
  loc_00414209: mov var_288, 00000008h
  loc_00414213: lea edx, var_158
  loc_00414219: push edx
  loc_0041421A: lea eax, var_148
  loc_00414220: push eax
  loc_00414221: lea ecx, var_168
  loc_00414227: push ecx
  loc_00414228: call [004011ACh] ; __vbaVarAdd
  loc_0041422E: push eax
  loc_0041422F: lea edx, var_258
  loc_00414235: push edx
  loc_00414236: lea eax, var_178
  loc_0041423C: push eax
  loc_0041423D: call [004011ACh] ; __vbaVarAdd
  loc_00414243: push eax
  loc_00414244: lea ecx, var_198
  loc_0041424A: push ecx
  loc_0041424B: lea edx, var_1A8
  loc_00414251: push edx
  loc_00414252: call [004011ACh] ; __vbaVarAdd
  loc_00414258: push eax
  loc_00414259: lea eax, var_268
  loc_0041425F: push eax
  loc_00414260: lea ecx, var_1B8
  loc_00414266: push ecx
  loc_00414267: call [004011ACh] ; __vbaVarAdd
  loc_0041426D: push eax
  loc_0041426E: lea edx, var_1D8
  loc_00414274: push edx
  loc_00414275: lea eax, var_1E8
  loc_0041427B: push eax
  loc_0041427C: call [004011ACh] ; __vbaVarAdd
  loc_00414282: push eax
  loc_00414283: lea ecx, var_278
  loc_00414289: push ecx
  loc_0041428A: lea edx, var_1F8
  loc_00414290: push edx
  loc_00414291: call [004011ACh] ; __vbaVarAdd
  loc_00414297: push eax
  loc_00414298: lea eax, var_218
  loc_0041429E: push eax
  loc_0041429F: lea ecx, var_228
  loc_004142A5: push ecx
  loc_004142A6: call [004011ACh] ; __vbaVarAdd
  loc_004142AC: push eax
  loc_004142AD: lea edx, var_288
  loc_004142B3: push edx
  loc_004142B4: lea eax, var_238
  loc_004142BA: push eax
  loc_004142BB: call [004011ACh] ; __vbaVarAdd
  loc_004142C1: push eax
  loc_004142C2: call [00401030h] ; __vbaStrVarMove
  loc_004142C8: mov edx, eax
  loc_004142CA: lea ecx, var_D8
  loc_004142D0: call [004011D0h] ; __vbaStrMove
  loc_004142D6: lea ecx, var_248
  loc_004142DC: push ecx
  loc_004142DD: lea edx, var_D8
  loc_004142E3: push edx
  loc_004142E4: mov eax, Me
  loc_004142E7: mov ecx, [eax]
  loc_004142E9: mov edx, Me
  loc_004142EC: push edx
  loc_004142ED: call [ecx+0000072Ch]
  loc_004142F3: lea eax, var_D8
  loc_004142F9: push eax
  loc_004142FA: lea ecx, var_D4
  loc_00414300: push ecx
  loc_00414301: lea edx, var_CC
  loc_00414307: push edx
  loc_00414308: lea eax, var_D0
  loc_0041430E: push eax
  loc_0041430F: lea ecx, var_C8
  loc_00414315: push ecx
  loc_00414316: push 00000005h
  loc_00414318: call [00401180h] ; __vbaFreeStrList
  loc_0041431E: add esp, 00000018h
  loc_00414321: lea edx, var_11C
  loc_00414327: push edx
  loc_00414328: lea eax, var_118
  loc_0041432E: push eax
  loc_0041432F: push 00000002h
  loc_00414331: call [00401040h] ; __vbaFreeObjList
  loc_00414337: add esp, 0000000Ch
  loc_0041433A: lea ecx, var_248
  loc_00414340: push ecx
  loc_00414341: lea edx, var_238
  loc_00414347: push edx
  loc_00414348: lea eax, var_228
  loc_0041434E: push eax
  loc_0041434F: lea ecx, var_218
  loc_00414355: push ecx
  loc_00414356: lea edx, var_1F8
  loc_0041435C: push edx
  loc_0041435D: lea eax, var_208
  loc_00414363: push eax
  loc_00414364: lea ecx, var_1E8
  loc_0041436A: push ecx
  loc_0041436B: lea edx, var_1D8
  loc_00414371: push edx
  loc_00414372: lea eax, var_1B8
  loc_00414378: push eax
  loc_00414379: lea ecx, var_1C8
  loc_0041437F: push ecx
  loc_00414380: lea edx, var_1A8
  loc_00414386: push edx
  loc_00414387: lea eax, var_198
  loc_0041438D: push eax
  loc_0041438E: lea ecx, var_178
  loc_00414394: push ecx
  loc_00414395: lea edx, var_188
  loc_0041439B: push edx
  loc_0041439C: lea eax, var_168
  loc_004143A2: push eax
  loc_004143A3: lea ecx, var_148
  loc_004143A9: push ecx
  loc_004143AA: lea edx, var_158
  loc_004143B0: push edx
  loc_004143B1: lea eax, var_138
  loc_004143B7: push eax
  loc_004143B8: push 00000012h
  loc_004143BA: call [00401038h] ; __vbaFreeVarList
  loc_004143C0: add esp, 0000004Ch
  loc_004143C3: mov ecx, Me
  loc_004143C6: mov edx, [ecx]
  loc_004143C8: mov eax, Me
  loc_004143CB: push eax
  loc_004143CC: call [edx+00000370h]
  loc_004143D2: push eax
  loc_004143D3: lea ecx, var_118
  loc_004143D9: push ecx
  loc_004143DA: call [00401080h] ; __vbaObjSet
  loc_004143E0: mov var_2C0, eax
  loc_004143E6: lea edx, var_C8
  loc_004143EC: push edx
  loc_004143ED: mov eax, var_2C0
  loc_004143F3: mov ecx, [eax]
  loc_004143F5: mov edx, var_2C0
  loc_004143FB: push edx
  loc_004143FC: call [ecx+000000A8h]
  loc_00414402: fnclex
  loc_00414404: mov var_2C4, eax
  loc_0041440A: cmp var_2C4, 00000000h
  loc_00414411: jge 00414439h
  loc_00414413: push 000000A8h
  loc_00414418: push 004055DCh
  loc_0041441D: mov eax, var_2C0
  loc_00414423: push eax
  loc_00414424: mov ecx, var_2C4
  loc_0041442A: push ecx
  loc_0041442B: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00414431: mov var_5E4, eax
  loc_00414437: jmp 00414443h
  loc_00414439: mov var_5E4, 00000000h
  loc_00414443: mov edx, Me
  loc_00414446: mov eax, [edx]
  loc_00414448: mov ecx, Me
  loc_0041444B: push ecx
  loc_0041444C: call [eax+00000324h]
  loc_00414452: push eax
  loc_00414453: lea edx, var_11C
  loc_00414459: push edx
  loc_0041445A: call [00401080h] ; __vbaObjSet
  loc_00414460: mov var_2C8, eax
  loc_00414466: lea eax, var_CC
  loc_0041446C: push eax
  loc_0041446D: mov ecx, var_2C8
  loc_00414473: mov edx, [ecx]
  loc_00414475: mov eax, var_2C8
  loc_0041447B: push eax
  loc_0041447C: call [edx+000000A8h]
  loc_00414482: fnclex
  loc_00414484: mov var_2CC, eax
  loc_0041448A: cmp var_2CC, 00000000h
  loc_00414491: jge 004144B9h
  loc_00414493: push 000000A8h
  loc_00414498: push 004055DCh
  loc_0041449D: mov ecx, var_2C8
  loc_004144A3: push ecx
  loc_004144A4: mov edx, var_2CC
  loc_004144AA: push edx
  loc_004144AB: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004144B1: mov var_5E8, eax
  loc_004144B7: jmp 004144C3h
  loc_004144B9: mov var_5E8, 00000000h
  loc_004144C3: mov eax, var_64
  loc_004144C6: push eax
  loc_004144C7: call [00401018h] ; __vbaStrI4
  loc_004144CD: mov var_130, eax
  loc_004144D3: mov var_138, 00000008h
  loc_004144DD: lea ecx, var_138
  loc_004144E3: push ecx
  loc_004144E4: lea edx, var_148
  loc_004144EA: push edx
  loc_004144EB: call [004010A4h] ; rtcTrimVar
  loc_004144F1: mov eax, var_60
  loc_004144F4: push eax
  loc_004144F5: call [00401018h] ; __vbaStrI4
  loc_004144FB: mov var_180, eax
  loc_00414501: mov var_188, 00000008h
  loc_0041450B: lea ecx, var_188
  loc_00414511: push ecx
  loc_00414512: lea edx, var_198
  loc_00414518: push edx
  loc_00414519: call [004010A4h] ; rtcTrimVar
  loc_0041451F: mov eax, var_60
  loc_00414522: sub eax, 00000001h
  loc_00414525: mov var_2D0, eax
  loc_0041452B: cmp var_2D0, 00000004h
  loc_00414532: jae 00414540h
  loc_00414534: mov var_5EC, 00000000h
  loc_0041453E: jmp 0041454Ch
  loc_00414540: call [004010D8h] ; __vbaGenerateBoundsError
  loc_00414546: mov var_5EC, eax
  loc_0041454C: mov ecx, var_2D0
  loc_00414552: mov edx, var_2C
  loc_00414555: mov eax, [edx+ecx*8+00000004h]
  loc_00414559: push eax
  loc_0041455A: mov ecx, [edx+ecx*8]
  loc_0041455D: push ecx
  loc_0041455E: call [00401104h] ; __vbaStrR8
  loc_00414564: mov var_1C0, eax
  loc_0041456A: mov var_1C8, 00000008h
  loc_00414574: lea edx, var_1C8
  loc_0041457A: push edx
  loc_0041457B: lea eax, var_1D8
  loc_00414581: push eax
  loc_00414582: call [004010A4h] ; rtcTrimVar
  loc_00414588: mov ecx, var_60
  loc_0041458B: sub ecx, 00000001h
  loc_0041458E: mov var_2D4, ecx
  loc_00414594: cmp var_2D4, 00000004h
  loc_0041459B: jae 004145A9h
  loc_0041459D: mov var_5F0, 00000000h
  loc_004145A7: jmp 004145B5h
  loc_004145A9: call [004010D8h] ; __vbaGenerateBoundsError
  loc_004145AF: mov var_5F0, eax
  loc_004145B5: mov edx, var_2D4
  loc_004145BB: mov eax, var_AC
  loc_004145C1: mov ecx, [eax+edx*8+00000004h]
  loc_004145C5: push ecx
  loc_004145C6: mov edx, [eax+edx*8]
  loc_004145C9: push edx
  loc_004145CA: call [00401104h] ; __vbaStrR8
  loc_004145D0: mov var_200, eax
  loc_004145D6: mov var_208, 00000008h
  loc_004145E0: lea eax, var_208
  loc_004145E6: push eax
  loc_004145E7: lea ecx, var_218
  loc_004145ED: push ecx
  loc_004145EE: call [004010A4h] ; rtcTrimVar
  loc_004145F4: mov edx, var_C8
  loc_004145FA: push edx
  loc_004145FB: push 00406D40h
  loc_00414600: call [00401050h] ; __vbaStrCat
  loc_00414606: mov edx, eax
  loc_00414608: lea ecx, var_D0
  loc_0041460E: call [004011D0h] ; __vbaStrMove
  loc_00414614: push eax
  loc_00414615: mov eax, var_CC
  loc_0041461B: push eax
  loc_0041461C: call [00401050h] ; __vbaStrCat
  loc_00414622: mov edx, eax
  loc_00414624: lea ecx, var_D4
  loc_0041462A: call [004011D0h] ; __vbaStrMove
  loc_00414630: push eax
  loc_00414631: push 00406D40h
  loc_00414636: call [00401050h] ; __vbaStrCat
  loc_0041463C: mov var_150, eax
  loc_00414642: mov var_158, 00000008h
  loc_0041464C: mov var_250, 00406D40h
  loc_00414656: mov var_258, 00000008h
  loc_00414660: mov var_260, 00406D40h
  loc_0041466A: mov var_268, 00000008h
  loc_00414674: mov var_270, 00406D40h
  loc_0041467E: mov var_278, 00000008h
  loc_00414688: mov var_280, 00406D40h
  loc_00414692: mov var_288, 00000008h
  loc_0041469C: lea ecx, var_158
  loc_004146A2: push ecx
  loc_004146A3: lea edx, var_148
  loc_004146A9: push edx
  loc_004146AA: lea eax, var_168
  loc_004146B0: push eax
  loc_004146B1: call [004011ACh] ; __vbaVarAdd
  loc_004146B7: push eax
  loc_004146B8: lea ecx, var_258
  loc_004146BE: push ecx
  loc_004146BF: lea edx, var_178
  loc_004146C5: push edx
  loc_004146C6: call [004011ACh] ; __vbaVarAdd
  loc_004146CC: push eax
  loc_004146CD: lea eax, var_198
  loc_004146D3: push eax
  loc_004146D4: lea ecx, var_1A8
  loc_004146DA: push ecx
  loc_004146DB: call [004011ACh] ; __vbaVarAdd
  loc_004146E1: push eax
  loc_004146E2: lea edx, var_268
  loc_004146E8: push edx
  loc_004146E9: lea eax, var_1B8
  loc_004146EF: push eax
  loc_004146F0: call [004011ACh] ; __vbaVarAdd
  loc_004146F6: push eax
  loc_004146F7: lea ecx, var_1D8
  loc_004146FD: push ecx
  loc_004146FE: lea edx, var_1E8
  loc_00414704: push edx
  loc_00414705: call [004011ACh] ; __vbaVarAdd
  loc_0041470B: push eax
  loc_0041470C: lea eax, var_278
  loc_00414712: push eax
  loc_00414713: lea ecx, var_1F8
  loc_00414719: push ecx
  loc_0041471A: call [004011ACh] ; __vbaVarAdd
  loc_00414720: push eax
  loc_00414721: lea edx, var_218
  loc_00414727: push edx
  loc_00414728: lea eax, var_228
  loc_0041472E: push eax
  loc_0041472F: call [004011ACh] ; __vbaVarAdd
  loc_00414735: push eax
  loc_00414736: lea ecx, var_288
  loc_0041473C: push ecx
  loc_0041473D: lea edx, var_238
  loc_00414743: push edx
  loc_00414744: call [004011ACh] ; __vbaVarAdd
  loc_0041474A: push eax
  loc_0041474B: call [00401030h] ; __vbaStrVarMove
  loc_00414751: mov edx, eax
  loc_00414753: lea ecx, var_D8
  loc_00414759: call [004011D0h] ; __vbaStrMove
  loc_0041475F: lea eax, var_248
  loc_00414765: push eax
  loc_00414766: lea ecx, var_D8
  loc_0041476C: push ecx
  loc_0041476D: mov edx, Me
  loc_00414770: mov eax, [edx]
  loc_00414772: mov ecx, Me
  loc_00414775: push ecx
  loc_00414776: call [eax+00000700h]
  loc_0041477C: mov var_2D8, eax
  loc_00414782: cmp var_2D8, 00000000h
  loc_00414789: jge 004147AEh
  loc_0041478B: push 00000700h
  loc_00414790: push 0040579Ch ; "#]=VｫoyAｷ ;ﾑs：ﾚLabel12"
  loc_00414795: mov edx, Me
  loc_00414798: push edx
  loc_00414799: mov eax, var_2D8
  loc_0041479F: push eax
  loc_004147A0: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004147A6: mov var_5F4, eax
  loc_004147AC: jmp 004147B8h
  loc_004147AE: mov var_5F4, 00000000h
  loc_004147B8: lea ecx, var_D8
  loc_004147BE: push ecx
  loc_004147BF: lea edx, var_D4
  loc_004147C5: push edx
  loc_004147C6: lea eax, var_CC
  loc_004147CC: push eax
  loc_004147CD: lea ecx, var_D0
  loc_004147D3: push ecx
  loc_004147D4: lea edx, var_C8
  loc_004147DA: push edx
  loc_004147DB: push 00000005h
  loc_004147DD: call [00401180h] ; __vbaFreeStrList
  loc_004147E3: add esp, 00000018h
  loc_004147E6: lea eax, var_11C
  loc_004147EC: push eax
  loc_004147ED: lea ecx, var_118
  loc_004147F3: push ecx
  loc_004147F4: push 00000002h
  loc_004147F6: call [00401040h] ; __vbaFreeObjList
  loc_004147FC: add esp, 0000000Ch
  loc_004147FF: lea edx, var_248
  loc_00414805: push edx
  loc_00414806: lea eax, var_238
  loc_0041480C: push eax
  loc_0041480D: lea ecx, var_228
  loc_00414813: push ecx
  loc_00414814: lea edx, var_218
  loc_0041481A: push edx
  loc_0041481B: lea eax, var_1F8
  loc_00414821: push eax
  loc_00414822: lea ecx, var_208
  loc_00414828: push ecx
  loc_00414829: lea edx, var_1E8
  loc_0041482F: push edx
  loc_00414830: lea eax, var_1D8
  loc_00414836: push eax
  loc_00414837: lea ecx, var_1B8
  loc_0041483D: push ecx
  loc_0041483E: lea edx, var_1C8
  loc_00414844: push edx
  loc_00414845: lea eax, var_1A8
  loc_0041484B: push eax
  loc_0041484C: lea ecx, var_198
  loc_00414852: push ecx
  loc_00414853: lea edx, var_178
  loc_00414859: push edx
  loc_0041485A: lea eax, var_188
  loc_00414860: push eax
  loc_00414861: lea ecx, var_168
  loc_00414867: push ecx
  loc_00414868: lea edx, var_148
  loc_0041486E: push edx
  loc_0041486F: lea eax, var_158
  loc_00414875: push eax
  loc_00414876: lea ecx, var_138
  loc_0041487C: push ecx
  loc_0041487D: push 00000012h
  loc_0041487F: call [00401038h] ; __vbaFreeVarList
  loc_00414885: add esp, 0000004Ch
  loc_00414888: jmp 004138B2h
  loc_0041488D: jmp 00413049h
  loc_00414892: lea edx, var_314
  loc_00414898: push edx
  loc_00414899: call [00401024h] ; __vbaGosubReturn
  loc_0041489F: mov var_4, 00000000h
  loc_004148A6: fwait
  loc_004148A7: push 00414A8Dh
  loc_004148AC: jmp 00414A0Dh
  loc_004148B1: lea eax, var_C4
  loc_004148B7: push eax
  loc_004148B8: call [004011E8h] ; __vbaAryUnlock
  loc_004148BE: lea ecx, var_114
  loc_004148C4: push ecx
  loc_004148C5: lea edx, var_110
  loc_004148CB: push edx
  loc_004148CC: lea eax, var_10C
  loc_004148D2: push eax
  loc_004148D3: lea ecx, var_108
  loc_004148D9: push ecx
  loc_004148DA: lea edx, var_104
  loc_004148E0: push edx
  loc_004148E1: lea eax, var_100
  loc_004148E7: push eax
  loc_004148E8: lea ecx, var_FC
  loc_004148EE: push ecx
  loc_004148EF: lea edx, var_F8
  loc_004148F5: push edx
  loc_004148F6: lea eax, var_F4
  loc_004148FC: push eax
  loc_004148FD: lea ecx, var_F0
  loc_00414903: push ecx
  loc_00414904: lea edx, var_EC
  loc_0041490A: push edx
  loc_0041490B: lea eax, var_E8
  loc_00414911: push eax
  loc_00414912: lea ecx, var_E4
  loc_00414918: push ecx
  loc_00414919: lea edx, var_E0
  loc_0041491F: push edx
  loc_00414920: lea eax, var_DC
  loc_00414926: push eax
  loc_00414927: lea ecx, var_D8
  loc_0041492D: push ecx
  loc_0041492E: lea edx, var_D4
  loc_00414934: push edx
  loc_00414935: lea eax, var_D0
  loc_0041493B: push eax
  loc_0041493C: lea ecx, var_CC
  loc_00414942: push ecx
  loc_00414943: lea edx, var_C8
  loc_00414949: push edx
  loc_0041494A: push 00000014h
  loc_0041494C: call [00401180h] ; __vbaFreeStrList
  loc_00414952: add esp, 00000054h
  loc_00414955: lea eax, var_128
  loc_0041495B: push eax
  loc_0041495C: lea ecx, var_124
  loc_00414962: push ecx
  loc_00414963: lea edx, var_120
  loc_00414969: push edx
  loc_0041496A: lea eax, var_11C
  loc_00414970: push eax
  loc_00414971: lea ecx, var_118
  loc_00414977: push ecx
  loc_00414978: push 00000005h
  loc_0041497A: call [00401040h] ; __vbaFreeObjList
  loc_00414980: add esp, 00000018h
  loc_00414983: lea edx, var_248
  loc_00414989: push edx
  loc_0041498A: lea eax, var_238
  loc_00414990: push eax
  loc_00414991: lea ecx, var_228
  loc_00414997: push ecx
  loc_00414998: lea edx, var_218
  loc_0041499E: push edx
  loc_0041499F: lea eax, var_208
  loc_004149A5: push eax
  loc_004149A6: lea ecx, var_1F8
  loc_004149AC: push ecx
  loc_004149AD: lea edx, var_1E8
  loc_004149B3: push edx
  loc_004149B4: lea eax, var_1D8
  loc_004149BA: push eax
  loc_004149BB: lea ecx, var_1C8
  loc_004149C1: push ecx
  loc_004149C2: lea edx, var_1B8
  loc_004149C8: push edx
  loc_004149C9: lea eax, var_1A8
  loc_004149CF: push eax
  loc_004149D0: lea ecx, var_198
  loc_004149D6: push ecx
  loc_004149D7: lea edx, var_188
  loc_004149DD: push edx
  loc_004149DE: lea eax, var_178
  loc_004149E4: push eax
  loc_004149E5: lea ecx, var_168
  loc_004149EB: push ecx
  loc_004149EC: lea edx, var_158
  loc_004149F2: push edx
  loc_004149F3: lea eax, var_148
  loc_004149F9: push eax
  loc_004149FA: lea ecx, var_138
  loc_00414A00: push ecx
  loc_00414A01: push 00000012h
  loc_00414A03: call [00401038h] ; __vbaFreeVarList
  loc_00414A09: add esp, 0000004Ch
  loc_00414A0C: ret
  loc_00414A0D: lea ecx, var_308
  loc_00414A13: call [00401020h] ; __vbaFreeVar
  loc_00414A19: lea edx, var_38
  loc_00414A1C: mov var_290, edx
  loc_00414A22: lea eax, var_290
  loc_00414A28: push eax
  loc_00414A29: push 00000000h
  loc_00414A2B: call [00401064h] ; __vbaAryDestruct
  loc_00414A31: lea ecx, var_40
  loc_00414A34: call [004011F4h] ; __vbaFreeStr
  loc_00414A3A: lea ecx, var_58
  loc_00414A3D: call [004011F4h] ; __vbaFreeStr
  loc_00414A43: lea ecx, var_5C
  loc_00414A46: call [004011F4h] ; __vbaFreeStr
  loc_00414A4C: lea ecx, var_84
  loc_00414A52: call [00401020h] ; __vbaFreeVar
  loc_00414A58: lea ecx, var_B8
  loc_00414A5E: mov var_294, ecx
  loc_00414A64: lea edx, var_294
  loc_00414A6A: push edx
  loc_00414A6B: push 00000000h
  loc_00414A6D: call [00401064h] ; __vbaAryDestruct
  loc_00414A73: lea ecx, var_C0
  loc_00414A79: call [004011F0h] ; __vbaFreeObj
  loc_00414A7F: lea eax, var_314
  loc_00414A85: push eax
  loc_00414A86: call [004010C8h] ; __vbaGosubFree
  loc_00414A8C: ret
  loc_00414A8D: mov ecx, Me
  loc_00414A90: mov edx, [ecx]
  loc_00414A92: mov eax, Me
  loc_00414A95: push eax
  loc_00414A96: call [edx+00000008h]
  loc_00414A99: mov eax, var_4
  loc_00414A9C: mov ecx, var_14
  loc_00414A9F: mov fs:[00000000h], ecx
  loc_00414AA6: pop edi
  loc_00414AA7: pop esi
  loc_00414AA8: pop ebx
  loc_00414AA9: mov esp, ebp
  loc_00414AAB: pop ebp
  loc_00414AAC: retn 0004h
End Sub

Private Sub LoadTimer_Timer() '418F10
  loc_00418F10: push ebp
  loc_00418F11: mov ebp, esp
  loc_00418F13: sub esp, 0000000Ch
  loc_00418F16: push 00401AA6h ; __vbaExceptHandler
  loc_00418F1B: mov eax, fs:[00000000h]
  loc_00418F21: push eax
  loc_00418F22: mov fs:[00000000h], esp
  loc_00418F29: sub esp, 00000028h
  loc_00418F2C: push ebx
  loc_00418F2D: push esi
  loc_00418F2E: push edi
  loc_00418F2F: mov var_C, esp
  loc_00418F32: mov var_8, 004015D8h
  loc_00418F39: mov esi, Me
  loc_00418F3C: mov eax, esi
  loc_00418F3E: and eax, 00000001h
  loc_00418F41: mov var_4, eax
  loc_00418F44: and esi, FFFFFFFEh
  loc_00418F47: push esi
  loc_00418F48: mov Me, esi
  loc_00418F4B: mov ecx, [esi]
  loc_00418F4D: call [ecx+00000004h]
  loc_00418F50: mov edx, [esi]
  loc_00418F52: xor eax, eax
  loc_00418F54: push esi
  loc_00418F55: mov var_18, eax
  loc_00418F58: mov var_1C, eax
  loc_00418F5B: mov var_20, eax
  loc_00418F5E: mov var_24, eax
  loc_00418F61: call [edx+0000039Ch]
  loc_00418F67: mov ebx, [00401080h] ; __vbaObjSet
  loc_00418F6D: push eax
  loc_00418F6E: lea eax, var_24
  loc_00418F71: push eax
  loc_00418F72: call ebx
  loc_00418F74: mov ecx, [esi]
  loc_00418F76: push esi
  loc_00418F77: mov edi, eax
  loc_00418F79: call [ecx+0000039Ch]
  loc_00418F7F: lea edx, var_20
  loc_00418F82: push eax
  loc_00418F83: push edx
  loc_00418F84: call ebx
  loc_00418F86: mov esi, eax
  loc_00418F88: lea ecx, var_18
  loc_00418F8B: push ecx
  loc_00418F8C: push esi
  loc_00418F8D: mov eax, [esi]
  loc_00418F8F: call [eax+00000050h]
  loc_00418F92: test eax, eax
  loc_00418F94: fnclex
  loc_00418F96: jge 00418FA7h
  loc_00418F98: push 00000050h
  loc_00418F9A: push 0040575Ch
  loc_00418F9F: push esi
  loc_00418FA0: push eax
  loc_00418FA1: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00418FA7: mov edx, var_18
  loc_00418FAA: mov esi, [edi]
  loc_00418FAC: push edx
  loc_00418FAD: push 00405AB4h ; "."
  loc_00418FB2: call [00401050h] ; __vbaStrCat
  loc_00418FB8: mov edx, eax
  loc_00418FBA: lea ecx, var_1C
  loc_00418FBD: call [004011D0h] ; __vbaStrMove
  loc_00418FC3: push eax
  loc_00418FC4: push edi
  loc_00418FC5: call [esi+00000054h]
  loc_00418FC8: test eax, eax
  loc_00418FCA: fnclex
  loc_00418FCC: jge 00418FDDh
  loc_00418FCE: push 00000054h
  loc_00418FD0: push 0040575Ch
  loc_00418FD5: push edi
  loc_00418FD6: push eax
  loc_00418FD7: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00418FDD: lea eax, var_1C
  loc_00418FE0: lea ecx, var_18
  loc_00418FE3: push eax
  loc_00418FE4: push ecx
  loc_00418FE5: push 00000002h
  loc_00418FE7: call [00401180h] ; __vbaFreeStrList
  loc_00418FED: lea edx, var_24
  loc_00418FF0: lea eax, var_20
  loc_00418FF3: push edx
  loc_00418FF4: push eax
  loc_00418FF5: push 00000002h
  loc_00418FF7: call [00401040h] ; __vbaFreeObjList
  loc_00418FFD: add esp, 00000018h
  loc_00419000: mov var_4, 00000000h
  loc_00419007: push 00419033h
  loc_0041900C: jmp 00419032h
  loc_0041900E: lea ecx, var_1C
  loc_00419011: lea edx, var_18
  loc_00419014: push ecx
  loc_00419015: push edx
  loc_00419016: push 00000002h
  loc_00419018: call [00401180h] ; __vbaFreeStrList
  loc_0041901E: lea eax, var_24
  loc_00419021: lea ecx, var_20
  loc_00419024: push eax
  loc_00419025: push ecx
  loc_00419026: push 00000002h
  loc_00419028: call [00401040h] ; __vbaFreeObjList
  loc_0041902E: add esp, 00000018h
  loc_00419031: ret
  loc_00419032: ret
  loc_00419033: mov eax, Me
  loc_00419036: push eax
  loc_00419037: mov edx, [eax]
  loc_00419039: call [edx+00000008h]
  loc_0041903C: mov eax, var_4
  loc_0041903F: mov ecx, var_14
  loc_00419042: pop edi
  loc_00419043: pop esi
  loc_00419044: mov fs:[00000000h], ecx
  loc_0041904B: pop ebx
  loc_0041904C: mov esp, ebp
  loc_0041904E: pop ebp
  loc_0041904F: retn 0004h
End Sub

Private Sub cmdView_Click() '414C60
  loc_00414C60: push ebp
  loc_00414C61: mov ebp, esp
  loc_00414C63: sub esp, 0000000Ch
  loc_00414C66: push 00401AA6h ; __vbaExceptHandler
  loc_00414C6B: mov eax, fs:[00000000h]
  loc_00414C71: push eax
  loc_00414C72: mov fs:[00000000h], esp
  loc_00414C79: sub esp, 00000098h
  loc_00414C7F: push ebx
  loc_00414C80: push esi
  loc_00414C81: push edi
  loc_00414C82: mov var_C, esp
  loc_00414C85: mov var_8, 004012B0h
  loc_00414C8C: mov esi, Me
  loc_00414C8F: mov eax, esi
  loc_00414C91: and eax, 00000001h
  loc_00414C94: mov var_4, eax
  loc_00414C97: and esi, FFFFFFFEh
  loc_00414C9A: push esi
  loc_00414C9B: mov Me, esi
  loc_00414C9E: mov ecx, [esi]
  loc_00414CA0: call [ecx+00000004h]
  loc_00414CA3: mov edx, [esi]
  loc_00414CA5: xor edi, edi
  loc_00414CA7: push esi
  loc_00414CA8: mov var_18, edi
  loc_00414CAB: mov var_1C, edi
  loc_00414CAE: mov var_20, edi
  loc_00414CB1: mov var_24, edi
  loc_00414CB4: mov var_34, edi
  loc_00414CB7: mov var_44, edi
  loc_00414CBA: mov var_54, edi
  loc_00414CBD: mov var_64, edi
  loc_00414CC0: mov var_74, edi
  loc_00414CC3: call [edx+0000037Ch]
  loc_00414CC9: mov var_2C, eax
  loc_00414CCC: lea eax, var_34
  loc_00414CCF: push edi
  loc_00414CD0: push eax
  loc_00414CD1: mov var_34, 00000009h
  loc_00414CD8: call [00401150h] ; rtcDir
  loc_00414CDE: mov ebx, [004011D0h] ; __vbaStrMove
  loc_00414CE4: mov edx, eax
  loc_00414CE6: lea ecx, var_18
  loc_00414CE9: call ebx
  loc_00414CEB: lea ecx, var_34
  loc_00414CEE: call [00401020h] ; __vbaFreeVar
  loc_00414CF4: mov ecx, var_18
  loc_00414CF7: push ecx
  loc_00414CF8: push edi
  loc_00414CF9: call [004010DCh] ; __vbaStrCmp
  loc_00414CFF: mov edx, [esi]
  loc_00414D01: push esi
  loc_00414D02: test eax, eax
  loc_00414D04: jz 00414D85h
  loc_00414D06: call [edx+0000037Ch]
  loc_00414D0C: push eax
  loc_00414D0D: lea eax, var_24
  loc_00414D10: push eax
  loc_00414D11: call [00401080h] ; __vbaObjSet
  loc_00414D17: mov esi, eax
  loc_00414D19: lea edx, var_1C
  loc_00414D1C: push edx
  loc_00414D1D: push esi
  loc_00414D1E: mov ecx, [esi]
  loc_00414D20: call [ecx+000000A0h]
  loc_00414D26: cmp eax, edi
  loc_00414D28: fnclex
  loc_00414D2A: jge 00414D3Eh
  loc_00414D2C: push 000000A0h
  loc_00414D31: push 00405398h
  loc_00414D36: push esi
  loc_00414D37: push eax
  loc_00414D38: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00414D3E: mov eax, var_1C
  loc_00414D41: push 00406E40h ; "C:\Windows\Notepad.exe "
  loc_00414D46: push eax
  loc_00414D47: call [00401050h] ; __vbaStrCat
  loc_00414D4D: lea ecx, var_34
  loc_00414D50: push 00000001h
  loc_00414D52: push ecx
  loc_00414D53: mov var_2C, eax
  loc_00414D56: mov var_34, 00000008h
  loc_00414D5D: call [00401114h] ; rtcShell
  loc_00414D63: lea ecx, var_1C
  loc_00414D66: fstp st0
  loc_00414D68: call [004011F4h] ; __vbaFreeStr
  loc_00414D6E: lea ecx, var_24
  loc_00414D71: call [004011F0h] ; __vbaFreeObj
  loc_00414D77: lea ecx, var_34
  loc_00414D7A: call [00401020h] ; __vbaFreeVar
  loc_00414D80: jmp 00414E66h
  loc_00414D85: call [edx+0000037Ch]
  loc_00414D8B: push eax
  loc_00414D8C: lea eax, var_24
  loc_00414D8F: push eax
  loc_00414D90: call [00401080h] ; __vbaObjSet
  loc_00414D96: mov esi, eax
  loc_00414D98: lea edx, var_1C
  loc_00414D9B: push edx
  loc_00414D9C: push esi
  loc_00414D9D: mov ecx, [esi]
  loc_00414D9F: call [ecx+000000A0h]
  loc_00414DA5: cmp eax, edi
  loc_00414DA7: fnclex
  loc_00414DA9: jge 00414DBDh
  loc_00414DAB: push 000000A0h
  loc_00414DB0: push 00405398h
  loc_00414DB5: push esi
  loc_00414DB6: push eax
  loc_00414DB7: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00414DBD: mov ecx, 80020004h
  loc_00414DC2: mov eax, 0000000Ah
  loc_00414DC7: mov var_5C, ecx
  loc_00414DCA: mov var_4C, ecx
  loc_00414DCD: lea edx, var_74
  loc_00414DD0: lea ecx, var_44
  loc_00414DD3: mov var_64, eax
  loc_00414DD6: mov var_54, eax
  loc_00414DD9: mov var_6C, 004050E8h ; "IMT LampElectrical Probing"
  loc_00414DE0: mov var_74, 00000008h
  loc_00414DE7: call [004011B4h] ; __vbaVarDup
  loc_00414DED: mov eax, var_1C
  loc_00414DF0: mov esi, [00401050h] ; __vbaStrCat
  loc_00414DF6: push 00406E74h ; "The data file '"
  loc_00414DFB: push eax
  loc_00414DFC: call __vbaStrCat
  loc_00414DFE: mov edx, eax
  loc_00414E00: lea ecx, var_20
  loc_00414E03: call ebx
  loc_00414E05: push eax
  loc_00414E06: push 00406E98h ; "' cannot be found!"
  loc_00414E0B: call __vbaStrCat
  loc_00414E0D: lea ecx, var_64
  loc_00414E10: mov var_2C, eax
  loc_00414E13: lea edx, var_54
  loc_00414E16: push ecx
  loc_00414E17: lea eax, var_44
  loc_00414E1A: push edx
  loc_00414E1B: push eax
  loc_00414E1C: lea ecx, var_34
  loc_00414E1F: push 00000030h
  loc_00414E21: push ecx
  loc_00414E22: mov var_34, 00000008h
  loc_00414E29: call [00401084h] ; rtcMsgBox
  loc_00414E2F: lea edx, var_20
  loc_00414E32: lea eax, var_1C
  loc_00414E35: push edx
  loc_00414E36: push eax
  loc_00414E37: push 00000002h
  loc_00414E39: call [00401180h] ; __vbaFreeStrList
  loc_00414E3F: add esp, 0000000Ch
  loc_00414E42: lea ecx, var_24
  loc_00414E45: call [004011F0h] ; __vbaFreeObj
  loc_00414E4B: lea ecx, var_64
  loc_00414E4E: lea edx, var_54
  loc_00414E51: push ecx
  loc_00414E52: lea eax, var_44
  loc_00414E55: push edx
  loc_00414E56: lea ecx, var_34
  loc_00414E59: push eax
  loc_00414E5A: push ecx
  loc_00414E5B: push 00000004h
  loc_00414E5D: call [00401038h] ; __vbaFreeVarList
  loc_00414E63: add esp, 00000014h
  loc_00414E66: mov var_4, edi
  loc_00414E69: fwait
  loc_00414E6A: push 00414EB3h
  loc_00414E6F: jmp 00414EA9h
  loc_00414E71: lea edx, var_20
  loc_00414E74: lea eax, var_1C
  loc_00414E77: push edx
  loc_00414E78: push eax
  loc_00414E79: push 00000002h
  loc_00414E7B: call [00401180h] ; __vbaFreeStrList
  loc_00414E81: add esp, 0000000Ch
  loc_00414E84: lea ecx, var_24
  loc_00414E87: call [004011F0h] ; __vbaFreeObj
  loc_00414E8D: lea ecx, var_64
  loc_00414E90: lea edx, var_54
  loc_00414E93: push ecx
  loc_00414E94: lea eax, var_44
  loc_00414E97: push edx
  loc_00414E98: lea ecx, var_34
  loc_00414E9B: push eax
  loc_00414E9C: push ecx
  loc_00414E9D: push 00000004h
  loc_00414E9F: call [00401038h] ; __vbaFreeVarList
  loc_00414EA5: add esp, 00000014h
  loc_00414EA8: ret
  loc_00414EA9: lea ecx, var_18
  loc_00414EAC: call [004011F4h] ; __vbaFreeStr
  loc_00414EB2: ret
  loc_00414EB3: mov eax, Me
  loc_00414EB6: push eax
  loc_00414EB7: mov edx, [eax]
  loc_00414EB9: call [edx+00000008h]
  loc_00414EBC: mov eax, var_4
  loc_00414EBF: mov ecx, var_14
  loc_00414EC2: pop edi
  loc_00414EC3: pop esi
  loc_00414EC4: mov fs:[00000000h], ecx
  loc_00414ECB: pop ebx
  loc_00414ECC: mov esp, ebp
  loc_00414ECE: pop ebp
  loc_00414ECF: retn 0004h
End Sub

Private Sub Form_Load() '414EE0
  loc_00414EE0: push ebp
  loc_00414EE1: mov ebp, esp
  loc_00414EE3: sub esp, 00000018h
  loc_00414EE6: push 00401AA6h ; __vbaExceptHandler
  loc_00414EEB: mov eax, fs:[00000000h]
  loc_00414EF1: push eax
  loc_00414EF2: mov fs:[00000000h], esp
  loc_00414EF9: mov eax, 00000364h
  loc_00414EFE: call 00401AA0h ; __vbaChkstk
  loc_00414F03: push ebx
  loc_00414F04: push esi
  loc_00414F05: push edi
  loc_00414F06: mov var_18, esp
  loc_00414F09: mov var_14, 004012C0h
  loc_00414F10: mov eax, Me
  loc_00414F13: and eax, 00000001h
  loc_00414F16: mov var_10, eax
  loc_00414F19: mov ecx, Me
  loc_00414F1C: and ecx, FFFFFFFEh
  loc_00414F1F: mov Me, ecx
  loc_00414F22: mov var_C, 00000000h
  loc_00414F29: mov edx, Me
  loc_00414F2C: mov eax, [edx]
  loc_00414F2E: mov ecx, Me
  loc_00414F31: push ecx
  loc_00414F32: call [eax+00000004h]
  loc_00414F35: mov var_4, 00000001h
  loc_00414F3C: mov var_4, 00000002h
  loc_00414F43: cmp [00423010h], 00000000h
  loc_00414F4A: jnz 00414F68h
  loc_00414F4C: push 00423010h
  loc_00414F51: push 004025D8h
  loc_00414F56: call [00401168h] ; __vbaNew2
  loc_00414F5C: mov var_224, 00423010h
  loc_00414F66: jmp 00414F72h
  loc_00414F68: mov var_224, 00423010h
  loc_00414F72: mov edx, var_224
  loc_00414F78: mov eax, [edx]
  loc_00414F7A: mov ecx, var_224
  loc_00414F80: mov edx, [ecx]
  loc_00414F82: mov ecx, [edx]
  loc_00414F84: push eax
  loc_00414F85: call [ecx+00000304h]
  loc_00414F8B: push eax
  loc_00414F8C: lea edx, var_64
  loc_00414F8F: push edx
  loc_00414F90: call [00401080h] ; __vbaObjSet
  loc_00414F96: mov var_1B8, eax
  loc_00414F9C: lea eax, var_4C
  loc_00414F9F: push eax
  loc_00414FA0: mov ecx, var_1B8
  loc_00414FA6: mov edx, [ecx]
  loc_00414FA8: mov eax, var_1B8
  loc_00414FAE: push eax
  loc_00414FAF: call [edx+000000A8h]
  loc_00414FB5: fnclex
  loc_00414FB7: mov var_1BC, eax
  loc_00414FBD: cmp var_1BC, 00000000h
  loc_00414FC4: jge 00414FECh
  loc_00414FC6: push 000000A8h
  loc_00414FCB: push 004055DCh
  loc_00414FD0: mov ecx, var_1B8
  loc_00414FD6: push ecx
  loc_00414FD7: mov edx, var_1BC
  loc_00414FDD: push edx
  loc_00414FDE: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00414FE4: mov var_228, eax
  loc_00414FEA: jmp 00414FF6h
  loc_00414FEC: mov var_228, 00000000h
  loc_00414FF6: mov edx, var_4C
  loc_00414FF9: mov ecx, Me
  loc_00414FFC: add ecx, 00000034h
  loc_00414FFF: call [00401178h] ; __vbaStrCopy
  loc_00415005: lea ecx, var_4C
  loc_00415008: call [004011F4h] ; __vbaFreeStr
  loc_0041500E: lea ecx, var_64
  loc_00415011: call [004011F0h] ; __vbaFreeObj
  loc_00415017: mov var_4, 00000003h
  loc_0041501E: mov eax, Me
  loc_00415021: mov ecx, [eax]
  loc_00415023: mov edx, Me
  loc_00415026: push edx
  loc_00415027: call [ecx+00000394h]
  loc_0041502D: push eax
  loc_0041502E: lea eax, var_64
  loc_00415031: push eax
  loc_00415032: call [00401080h] ; __vbaObjSet
  loc_00415038: mov var_1B8, eax
  loc_0041503E: push 000000FAh
  loc_00415043: mov ecx, var_1B8
  loc_00415049: mov edx, [ecx]
  loc_0041504B: mov eax, var_1B8
  loc_00415051: push eax
  loc_00415052: call [edx+00000064h]
  loc_00415055: fnclex
  loc_00415057: mov var_1BC, eax
  loc_0041505D: cmp var_1BC, 00000000h
  loc_00415064: jge 00415089h
  loc_00415066: push 00000064h
  loc_00415068: push 004056F4h
  loc_0041506D: mov ecx, var_1B8
  loc_00415073: push ecx
  loc_00415074: mov edx, var_1BC
  loc_0041507A: push edx
  loc_0041507B: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00415081: mov var_22C, eax
  loc_00415087: jmp 00415093h
  loc_00415089: mov var_22C, 00000000h
  loc_00415093: lea ecx, var_64
  loc_00415096: call [004011F0h] ; __vbaFreeObj
  loc_0041509C: mov var_4, 00000004h
  loc_004150A3: mov eax, Me
  loc_004150A6: mov ecx, [eax]
  loc_004150A8: mov edx, Me
  loc_004150AB: push edx
  loc_004150AC: call [ecx+00000394h]
  loc_004150B2: push eax
  loc_004150B3: lea eax, var_64
  loc_004150B6: push eax
  loc_004150B7: call [00401080h] ; __vbaObjSet
  loc_004150BD: mov var_1B8, eax
  loc_004150C3: push FFFFFFFFh
  loc_004150C5: mov ecx, var_1B8
  loc_004150CB: mov edx, [ecx]
  loc_004150CD: mov eax, var_1B8
  loc_004150D3: push eax
  loc_004150D4: call [edx+0000005Ch]
  loc_004150D7: fnclex
  loc_004150D9: mov var_1BC, eax
  loc_004150DF: cmp var_1BC, 00000000h
  loc_004150E6: jge 0041510Bh
  loc_004150E8: push 0000005Ch
  loc_004150EA: push 004056F4h
  loc_004150EF: mov ecx, var_1B8
  loc_004150F5: push ecx
  loc_004150F6: mov edx, var_1BC
  loc_004150FC: push edx
  loc_004150FD: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00415103: mov var_230, eax
  loc_00415109: jmp 00415115h
  loc_0041510B: mov var_230, 00000000h
  loc_00415115: lea ecx, var_64
  loc_00415118: call [004011F0h] ; __vbaFreeObj
  loc_0041511E: mov var_4, 00000005h
  loc_00415125: mov eax, Me
  loc_00415128: mov ecx, [eax]
  loc_0041512A: mov edx, Me
  loc_0041512D: push edx
  loc_0041512E: call [ecx+0000039Ch]
  loc_00415134: push eax
  loc_00415135: lea eax, var_64
  loc_00415138: push eax
  loc_00415139: call [00401080h] ; __vbaObjSet
  loc_0041513F: mov var_1B8, eax
  loc_00415145: push 00406EE4h ; "Loading, please wait"
  loc_0041514A: mov ecx, var_1B8
  loc_00415150: mov edx, [ecx]
  loc_00415152: mov eax, var_1B8
  loc_00415158: push eax
  loc_00415159: call [edx+00000054h]
  loc_0041515C: fnclex
  loc_0041515E: mov var_1BC, eax
  loc_00415164: cmp var_1BC, 00000000h
  loc_0041516B: jge 00415190h
  loc_0041516D: push 00000054h
  loc_0041516F: push 0040575Ch
  loc_00415174: mov ecx, var_1B8
  loc_0041517A: push ecx
  loc_0041517B: mov edx, var_1BC
  loc_00415181: push edx
  loc_00415182: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00415188: mov var_234, eax
  loc_0041518E: jmp 0041519Ah
  loc_00415190: mov var_234, 00000000h
  loc_0041519A: lea ecx, var_64
  loc_0041519D: call [004011F0h] ; __vbaFreeObj
  loc_004151A3: mov var_4, 00000006h
  loc_004151AA: push 00000001h
  loc_004151AC: call [0040107Ch] ; __vbaOnError
  loc_004151B2: mov var_4, 00000007h
  loc_004151B9: mov var_70, 80020004h
  loc_004151C0: mov var_78, 0000000Ah
  loc_004151C7: lea eax, var_78
  loc_004151CA: push eax
  loc_004151CB: call [00401164h] ; rtcFreeFile
  loc_004151D1: movsx ecx, ax
  loc_004151D4: mov var_30, ecx
  loc_004151D7: lea ecx, var_78
  loc_004151DA: call [00401020h] ; __vbaFreeVar
  loc_004151E0: mov var_4, 00000008h
  loc_004151E7: push FFFFFFFFh
  loc_004151E9: call [0040107Ch] ; __vbaOnError
  loc_004151EF: mov var_4, 00000009h
  loc_004151F6: push 00406F14h ; "C:\ProbeRecipe\LampElectrical\"
  loc_004151FB: mov edx, Me
  loc_004151FE: mov eax, [edx+00000034h]
  loc_00415201: push eax
  loc_00415202: call [00401050h] ; __vbaStrCat
  loc_00415208: mov edx, eax
  loc_0041520A: lea ecx, var_4C
  loc_0041520D: call [004011D0h] ; __vbaStrMove
  loc_00415213: push eax
  loc_00415214: push 00406F58h
  loc_00415219: call [00401050h] ; __vbaStrCat
  loc_0041521F: mov edx, eax
  loc_00415221: lea ecx, var_50
  loc_00415224: call [004011D0h] ; __vbaStrMove
  loc_0041522A: push eax
  loc_0041522B: mov ecx, var_30
  loc_0041522E: call [004010ECh] ; __vbaI2I4
  loc_00415234: push eax
  loc_00415235: push FFFFFFFFh
  loc_00415237: push 00004101h
  loc_0041523C: call [0040115Ch] ; __vbaFileOpen
  loc_00415242: lea ecx, var_50
  loc_00415245: push ecx
  loc_00415246: lea edx, var_4C
  loc_00415249: push edx
  loc_0041524A: push 00000002h
  loc_0041524C: call [00401180h] ; __vbaFreeStrList
  loc_00415252: add esp, 0000000Ch
  loc_00415255: mov var_4, 0000000Ah
  loc_0041525C: call [00401190h] ; rtcErrObj
  loc_00415262: push eax
  loc_00415263: lea eax, var_64
  loc_00415266: push eax
  loc_00415267: call [00401080h] ; __vbaObjSet
  loc_0041526D: mov var_1B8, eax
  loc_00415273: lea ecx, var_1B4
  loc_00415279: push ecx
  loc_0041527A: mov edx, var_1B8
  loc_00415280: mov eax, [edx]
  loc_00415282: mov ecx, var_1B8
  loc_00415288: push ecx
  loc_00415289: call [eax+0000001Ch]
  loc_0041528C: fnclex
  loc_0041528E: mov var_1BC, eax
  loc_00415294: cmp var_1BC, 00000000h
  loc_0041529B: jge 004152C0h
  loc_0041529D: push 0000001Ch
  loc_0041529F: push 00406F64h
  loc_004152A4: mov edx, var_1B8
  loc_004152AA: push edx
  loc_004152AB: mov eax, var_1BC
  loc_004152B1: push eax
  loc_004152B2: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004152B8: mov var_238, eax
  loc_004152BE: jmp 004152CAh
  loc_004152C0: mov var_238, 00000000h
  loc_004152CA: xor ecx, ecx
  loc_004152CC: cmp var_1B4, 00000000h
  loc_004152D3: setnz cl
  loc_004152D6: neg ecx
  loc_004152D8: mov var_1C0, cx
  loc_004152DF: lea ecx, var_64
  loc_004152E2: call [004011F0h] ; __vbaFreeObj
  loc_004152E8: movsx edx, var_1C0
  loc_004152EF: test edx, edx
  loc_004152F1: jz 004153E6h
  loc_004152F7: mov var_4, 0000000Bh
  loc_004152FE: mov var_A0, 80020004h
  loc_00415308: mov var_A8, 0000000Ah
  loc_00415312: mov var_90, 80020004h
  loc_0041531C: mov var_98, 0000000Ah
  loc_00415326: mov var_80, 80020004h
  loc_0041532D: mov var_88, 0000000Ah
  loc_00415337: push 00406F78h ; "Not found "
  loc_0041533C: push 00406F14h ; "C:\ProbeRecipe\LampElectrical\"
  loc_00415341: call [00401050h] ; __vbaStrCat
  loc_00415347: mov edx, eax
  loc_00415349: lea ecx, var_4C
  loc_0041534C: call [004011D0h] ; __vbaStrMove
  loc_00415352: push eax
  loc_00415353: mov eax, Me
  loc_00415356: mov ecx, [eax+00000034h]
  loc_00415359: push ecx
  loc_0041535A: call [00401050h] ; __vbaStrCat
  loc_00415360: mov edx, eax
  loc_00415362: lea ecx, var_50
  loc_00415365: call [004011D0h] ; __vbaStrMove
  loc_0041536B: push eax
  loc_0041536C: push 00406F58h
  loc_00415371: call [00401050h] ; __vbaStrCat
  loc_00415377: mov var_70, eax
  loc_0041537A: mov var_78, 00000008h
  loc_00415381: lea edx, var_A8
  loc_00415387: push edx
  loc_00415388: lea eax, var_98
  loc_0041538E: push eax
  loc_0041538F: lea ecx, var_88
  loc_00415395: push ecx
  loc_00415396: push 00000000h
  loc_00415398: lea edx, var_78
  loc_0041539B: push edx
  loc_0041539C: call [00401084h] ; rtcMsgBox
  loc_004153A2: lea eax, var_50
  loc_004153A5: push eax
  loc_004153A6: lea ecx, var_4C
  loc_004153A9: push ecx
  loc_004153AA: push 00000002h
  loc_004153AC: call [00401180h] ; __vbaFreeStrList
  loc_004153B2: add esp, 0000000Ch
  loc_004153B5: lea edx, var_A8
  loc_004153BB: push edx
  loc_004153BC: lea eax, var_98
  loc_004153C2: push eax
  loc_004153C3: lea ecx, var_88
  loc_004153C9: push ecx
  loc_004153CA: lea edx, var_78
  loc_004153CD: push edx
  loc_004153CE: push 00000004h
  loc_004153D0: call [00401038h] ; __vbaFreeVarList
  loc_004153D6: add esp, 00000014h
  loc_004153D9: mov var_4, 0000000Ch
  loc_004153E0: call [00401034h] ; __vbaEnd
  loc_004153E6: mov var_4, 0000000Eh
  loc_004153ED: push 00000001h
  loc_004153EF: call [0040107Ch] ; __vbaOnError
  loc_004153F5: mov var_4, 00000010h
  loc_004153FC: mov ecx, var_30
  loc_004153FF: call [004010ECh] ; __vbaI2I4
  loc_00415405: push eax
  loc_00415406: lea eax, var_2C
  loc_00415409: push eax
  loc_0041540A: call [00401028h] ; __vbaLineInputStr
  loc_00415410: mov var_4, 00000011h
  loc_00415417: mov ecx, Me
  loc_0041541A: mov edx, [ecx+00000038h]
  loc_0041541D: push edx
  loc_0041541E: mov eax, var_2C
  loc_00415421: push eax
  loc_00415422: call [00401050h] ; __vbaStrCat
  loc_00415428: mov edx, eax
  loc_0041542A: lea ecx, var_4C
  loc_0041542D: call [004011D0h] ; __vbaStrMove
  loc_00415433: push eax
  loc_00415434: push 00406D40h
  loc_00415439: call [00401050h] ; __vbaStrCat
  loc_0041543F: mov edx, eax
  loc_00415441: lea ecx, var_50
  loc_00415444: call [004011D0h] ; __vbaStrMove
  loc_0041544A: mov edx, eax
  loc_0041544C: mov ecx, Me
  loc_0041544F: add ecx, 00000038h
  loc_00415452: call [00401178h] ; __vbaStrCopy
  loc_00415458: lea ecx, var_50
  loc_0041545B: push ecx
  loc_0041545C: lea edx, var_4C
  loc_0041545F: push edx
  loc_00415460: push 00000002h
  loc_00415462: call [00401180h] ; __vbaFreeStrList
  loc_00415468: add esp, 0000000Ch
  loc_0041546B: jmp 004153F5h
  loc_0041546D: mov var_4, 00000014h
  loc_00415474: mov var_120, 00406FF4h ; "True"
  loc_0041547E: mov var_128, 00000008h
  loc_00415488: mov eax, 00000010h
  loc_0041548D: call 00401AA0h ; __vbaChkstk
  loc_00415492: mov eax, esp
  loc_00415494: mov ecx, var_128
  loc_0041549A: mov [eax], ecx
  loc_0041549C: mov edx, var_124
  loc_004154A2: mov [eax+00000004h], edx
  loc_004154A5: mov ecx, var_120
  loc_004154AB: mov [eax+00000008h], ecx
  loc_004154AE: mov edx, var_11C
  loc_004154B4: mov [eax+0000000Ch], edx
  loc_004154B7: push 00406FD0h ; "FlushActivated"
  loc_004154BC: push 00406FB8h ; "Settings"
  loc_004154C1: push 00406F94h ; "LampElectrical"
  loc_004154C6: call [004011A0h] ; rtcGetSetting
  loc_004154CC: mov edx, eax
  loc_004154CE: lea ecx, var_4C
  loc_004154D1: call [004011D0h] ; __vbaStrMove
  loc_004154D7: push eax
  loc_004154D8: call [00401070h] ; __vbaBoolStr
  loc_004154DE: xor ecx, ecx
  loc_004154E0: cmp ax, FFFFFFh
  loc_004154E4: setz cl
  loc_004154E7: neg ecx
  loc_004154E9: mov var_1B8, cx
  loc_004154F0: lea ecx, var_4C
  loc_004154F3: call [004011F4h] ; __vbaFreeStr
  loc_004154F9: movsx edx, var_1B8
  loc_00415500: test edx, edx
  loc_00415502: jz 0041559Ah
  loc_00415508: mov var_4, 00000015h
  loc_0041550F: mov eax, Me
  loc_00415512: mov ecx, [eax]
  loc_00415514: mov edx, Me
  loc_00415517: push edx
  loc_00415518: call [ecx+000002FCh]
  loc_0041551E: push eax
  loc_0041551F: lea eax, var_64
  loc_00415522: push eax
  loc_00415523: call [00401080h] ; __vbaObjSet
  loc_00415529: mov var_1B8, eax
  loc_0041552F: mov ecx, 00000001h
  loc_00415534: call [004010ECh] ; __vbaI2I4
  loc_0041553A: push eax
  loc_0041553B: mov ecx, var_1B8
  loc_00415541: mov edx, [ecx]
  loc_00415543: mov eax, var_1B8
  loc_00415549: push eax
  loc_0041554A: call [edx+000000E4h]
  loc_00415550: fnclex
  loc_00415552: mov var_1BC, eax
  loc_00415558: cmp var_1BC, 00000000h
  loc_0041555F: jge 00415587h
  loc_00415561: push 000000E4h
  loc_00415566: push 00405354h
  loc_0041556B: mov ecx, var_1B8
  loc_00415571: push ecx
  loc_00415572: mov edx, var_1BC
  loc_00415578: push edx
  loc_00415579: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041557F: mov var_23C, eax
  loc_00415585: jmp 00415591h
  loc_00415587: mov var_23C, 00000000h
  loc_00415591: lea ecx, var_64
  loc_00415594: call [004011F0h] ; __vbaFreeObj
  loc_0041559A: mov var_4, 00000017h
  loc_004155A1: push 00402208h
  loc_004155A6: call [00401110h] ; __vbaNew
  loc_004155AC: push eax
  loc_004155AD: lea eax, var_48
  loc_004155B0: push eax
  loc_004155B1: call [00401080h] ; __vbaObjSet
  loc_004155B7: mov var_4, 00000018h
  loc_004155BE: mov ecx, Me
  loc_004155C1: mov edx, [ecx+00000038h]
  loc_004155C4: lea ecx, var_4C
  loc_004155C7: call [00401178h] ; __vbaStrCopy
  loc_004155CD: lea edx, var_4C
  loc_004155D0: push edx
  loc_004155D1: mov eax, var_48
  loc_004155D4: mov ecx, [eax]
  loc_004155D6: mov edx, var_48
  loc_004155D9: push edx
  loc_004155DA: call [ecx+00000038h]
  loc_004155DD: fnclex
  loc_004155DF: mov var_1B8, eax
  loc_004155E5: cmp var_1B8, 00000000h
  loc_004155EC: jge 0041560Eh
  loc_004155EE: push 00000038h
  loc_004155F0: push 00405B8Ch
  loc_004155F5: mov eax, var_48
  loc_004155F8: push eax
  loc_004155F9: mov ecx, var_1B8
  loc_004155FF: push ecx
  loc_00415600: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00415606: mov var_240, eax
  loc_0041560C: jmp 00415618h
  loc_0041560E: mov var_240, 00000000h
  loc_00415618: lea ecx, var_4C
  loc_0041561B: call [004011F4h] ; __vbaFreeStr
  loc_00415621: mov var_4, 00000019h
  loc_00415628: mov edx, 00407004h ; "CountMovesMajor"
  loc_0041562D: lea ecx, var_4C
  loc_00415630: call [00401178h] ; __vbaStrCopy
  loc_00415636: lea edx, var_50
  loc_00415639: push edx
  loc_0041563A: lea eax, var_4C
  loc_0041563D: push eax
  loc_0041563E: mov ecx, var_48
  loc_00415641: mov edx, [ecx]
  loc_00415643: mov eax, var_48
  loc_00415646: push eax
  loc_00415647: call [edx+0000002Ch]
  loc_0041564A: fnclex
  loc_0041564C: mov var_1B8, eax
  loc_00415652: cmp var_1B8, 00000000h
  loc_00415659: jge 0041567Bh
  loc_0041565B: push 0000002Ch
  loc_0041565D: push 00405B8Ch
  loc_00415662: mov ecx, var_48
  loc_00415665: push ecx
  loc_00415666: mov edx, var_1B8
  loc_0041566C: push edx
  loc_0041566D: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00415673: mov var_244, eax
  loc_00415679: jmp 00415685h
  loc_0041567B: mov var_244, 00000000h
  loc_00415685: mov eax, var_50
  loc_00415688: push eax
  loc_00415689: call [0040117Ch] ; __vbaI4Str
  loc_0041568F: mov ecx, Me
  loc_00415692: mov [ecx+00000054h], eax
  loc_00415695: lea edx, var_50
  loc_00415698: push edx
  loc_00415699: lea eax, var_4C
  loc_0041569C: push eax
  loc_0041569D: push 00000002h
  loc_0041569F: call [00401180h] ; __vbaFreeStrList
  loc_004156A5: add esp, 0000000Ch
  loc_004156A8: mov var_4, 0000001Ah
  loc_004156AF: mov edx, 00407028h ; "CountMovesMinor"
  loc_004156B4: lea ecx, var_4C
  loc_004156B7: call [00401178h] ; __vbaStrCopy
  loc_004156BD: lea ecx, var_50
  loc_004156C0: push ecx
  loc_004156C1: lea edx, var_4C
  loc_004156C4: push edx
  loc_004156C5: mov eax, var_48
  loc_004156C8: mov ecx, [eax]
  loc_004156CA: mov edx, var_48
  loc_004156CD: push edx
  loc_004156CE: call [ecx+0000002Ch]
  loc_004156D1: fnclex
  loc_004156D3: mov var_1B8, eax
  loc_004156D9: cmp var_1B8, 00000000h
  loc_004156E0: jge 00415702h
  loc_004156E2: push 0000002Ch
  loc_004156E4: push 00405B8Ch
  loc_004156E9: mov eax, var_48
  loc_004156EC: push eax
  loc_004156ED: mov ecx, var_1B8
  loc_004156F3: push ecx
  loc_004156F4: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004156FA: mov var_248, eax
  loc_00415700: jmp 0041570Ch
  loc_00415702: mov var_248, 00000000h
  loc_0041570C: mov edx, var_50
  loc_0041570F: push edx
  loc_00415710: call [0040117Ch] ; __vbaI4Str
  loc_00415716: mov ecx, Me
  loc_00415719: mov [ecx+00000058h], eax
  loc_0041571C: lea edx, var_50
  loc_0041571F: push edx
  loc_00415720: lea eax, var_4C
  loc_00415723: push eax
  loc_00415724: push 00000002h
  loc_00415726: call [00401180h] ; __vbaFreeStrList
  loc_0041572C: add esp, 0000000Ch
  loc_0041572F: mov var_4, 0000001Bh
  loc_00415736: call [004010A0h] ; rtcDoEvents
  loc_0041573C: mov var_4, 0000001Ch
  loc_00415743: push 00000000h
  loc_00415745: call [0040107Ch] ; __vbaOnError
  loc_0041574B: mov var_4, 0000001Dh
  loc_00415752: push 00000000h
  loc_00415754: mov ecx, Me
  loc_00415757: mov edx, [ecx+00000054h]
  loc_0041575A: sub edx, 00000001h
  loc_0041575D: jo 00418DF3h
  loc_00415763: push edx
  loc_00415764: push 00000001h
  loc_00415766: push 00000003h
  loc_00415768: mov eax, Me
  loc_0041576B: add eax, 0000003Ch
  loc_0041576E: push eax
  loc_0041576F: push 00000004h
  loc_00415771: push 00000080h
  loc_00415776: call [00401108h] ; __vbaRedim
  loc_0041577C: add esp, 0000001Ch
  loc_0041577F: mov var_4, 0000001Eh
  loc_00415786: push 00000000h
  loc_00415788: mov ecx, Me
  loc_0041578B: mov edx, [ecx+00000054h]
  loc_0041578E: sub edx, 00000001h
  loc_00415791: jo 00418DF3h
  loc_00415797: push edx
  loc_00415798: push 00000001h
  loc_0041579A: push 00000003h
  loc_0041579C: mov eax, Me
  loc_0041579F: add eax, 00000044h
  loc_004157A2: push eax
  loc_004157A3: push 00000004h
  loc_004157A5: push 00000080h
  loc_004157AA: call [00401108h] ; __vbaRedim
  loc_004157B0: add esp, 0000001Ch
  loc_004157B3: mov var_4, 0000001Fh
  loc_004157BA: push 00000000h
  loc_004157BC: mov ecx, Me
  loc_004157BF: mov edx, [ecx+00000054h]
  loc_004157C2: sub edx, 00000001h
  loc_004157C5: jo 00418DF3h
  loc_004157CB: push edx
  loc_004157CC: push 00000001h
  loc_004157CE: push 00000008h
  loc_004157D0: mov eax, Me
  loc_004157D3: add eax, 0000004Ch
  loc_004157D6: push eax
  loc_004157D7: push 00000004h
  loc_004157D9: push 00000180h
  loc_004157DE: call [00401108h] ; __vbaRedim
  loc_004157E4: add esp, 0000001Ch
  loc_004157E7: mov var_4, 00000020h
  loc_004157EE: mov var_70, 80020004h
  loc_004157F5: mov var_78, 0000000Ah
  loc_004157FC: lea ecx, var_78
  loc_004157FF: push ecx
  loc_00415800: call [00401164h] ; rtcFreeFile
  loc_00415806: movsx edx, ax
  loc_00415809: mov var_30, edx
  loc_0041580C: lea ecx, var_78
  loc_0041580F: call [00401020h] ; __vbaFreeVar
  loc_00415815: mov var_4, 00000021h
  loc_0041581C: mov edx, 0040704Ch ; "MovesMajor"
  loc_00415821: lea ecx, var_4C
  loc_00415824: call [00401178h] ; __vbaStrCopy
  loc_0041582A: lea eax, var_50
  loc_0041582D: push eax
  loc_0041582E: lea ecx, var_4C
  loc_00415831: push ecx
  loc_00415832: mov edx, var_48
  loc_00415835: mov eax, [edx]
  loc_00415837: mov ecx, var_48
  loc_0041583A: push ecx
  loc_0041583B: call [eax+0000002Ch]
  loc_0041583E: fnclex
  loc_00415840: mov var_1B8, eax
  loc_00415846: cmp var_1B8, 00000000h
  loc_0041584D: jge 0041586Fh
  loc_0041584F: push 0000002Ch
  loc_00415851: push 00405B8Ch
  loc_00415856: mov edx, var_48
  loc_00415859: push edx
  loc_0041585A: mov eax, var_1B8
  loc_00415860: push eax
  loc_00415861: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00415867: mov var_24C, eax
  loc_0041586D: jmp 00415879h
  loc_0041586F: mov var_24C, 00000000h
  loc_00415879: mov ecx, var_50
  loc_0041587C: push ecx
  loc_0041587D: push 00407068h ; "X.PMV"
  loc_00415882: call [00401050h] ; __vbaStrCat
  loc_00415888: mov edx, eax
  loc_0041588A: lea ecx, var_54
  loc_0041588D: call [004011D0h] ; __vbaStrMove
  loc_00415893: push eax
  loc_00415894: mov ecx, var_30
  loc_00415897: call [004010ECh] ; __vbaI2I4
  loc_0041589D: push eax
  loc_0041589E: push FFFFFFFFh
  loc_004158A0: push 00004101h
  loc_004158A5: call [0040115Ch] ; __vbaFileOpen
  loc_004158AB: lea edx, var_54
  loc_004158AE: push edx
  loc_004158AF: lea eax, var_50
  loc_004158B2: push eax
  loc_004158B3: lea ecx, var_4C
  loc_004158B6: push ecx
  loc_004158B7: push 00000003h
  loc_004158B9: call [00401180h] ; __vbaFreeStrList
  loc_004158BF: add esp, 00000010h
  loc_004158C2: mov var_4, 00000022h
  loc_004158C9: mov edx, Me
  loc_004158CC: mov ecx, [edx+00000054h]
  loc_004158CF: sub ecx, 00000001h
  loc_004158D2: jo 00418DF3h
  loc_004158D8: call [004010ECh] ; __vbaI2I4
  loc_004158DE: mov var_1D4, ax
  loc_004158E5: mov var_1D0, 0001h
  loc_004158EE: mov var_24, 0000h
  loc_004158F4: jmp 0041590Bh
  loc_004158F6: mov ax, var_24
  loc_004158FA: add ax, var_1D0
  loc_00415901: jo 00418DF3h
  loc_00415907: mov var_24, ax
  loc_0041590B: mov cx, var_24
  loc_0041590F: cmp cx, var_1D4
  loc_00415916: jg 004159D4h
  loc_0041591C: mov var_4, 00000023h
  loc_00415923: mov ecx, var_30
  loc_00415926: call [004010ECh] ; __vbaI2I4
  loc_0041592C: push eax
  loc_0041592D: lea edx, var_2C
  loc_00415930: push edx
  loc_00415931: call [00401028h] ; __vbaLineInputStr
  loc_00415937: mov var_4, 00000024h
  loc_0041593E: mov eax, Me
  loc_00415941: cmp [eax+0000003Ch], 00000000h
  loc_00415945: jz 004159A0h
  loc_00415947: mov ecx, Me
  loc_0041594A: mov edx, [ecx+0000003Ch]
  loc_0041594D: cmp [edx], 0001h
  loc_00415951: jnz 004159A0h
  loc_00415953: movsx eax, var_24
  loc_00415957: mov ecx, Me
  loc_0041595A: mov edx, [ecx+0000003Ch]
  loc_0041595D: sub eax, [edx+00000014h]
  loc_00415960: mov var_1B8, eax
  loc_00415966: mov eax, Me
  loc_00415969: mov ecx, [eax+0000003Ch]
  loc_0041596C: mov edx, var_1B8
  loc_00415972: cmp edx, [ecx+00000010h]
  loc_00415975: jae 00415983h
  loc_00415977: mov var_250, 00000000h
  loc_00415981: jmp 0041598Fh
  loc_00415983: call [004010D8h] ; __vbaGenerateBoundsError
  loc_00415989: mov var_250, eax
  loc_0041598F: mov eax, var_1B8
  loc_00415995: shl eax, 02h
  loc_00415998: mov var_254, eax
  loc_0041599E: jmp 004159ACh
  loc_004159A0: call [004010D8h] ; __vbaGenerateBoundsError
  loc_004159A6: mov var_254, eax
  loc_004159AC: mov ecx, var_2C
  loc_004159AF: push ecx
  loc_004159B0: call [0040117Ch] ; __vbaI4Str
  loc_004159B6: mov edx, Me
  loc_004159B9: mov ecx, [edx+0000003Ch]
  loc_004159BC: mov edx, [ecx+0000000Ch]
  loc_004159BF: mov ecx, var_254
  loc_004159C5: mov [edx+ecx], eax
  loc_004159C8: mov var_4, 00000025h
  loc_004159CF: jmp 004158F6h
  loc_004159D4: mov var_4, 00000026h
  loc_004159DB: mov ecx, var_30
  loc_004159DE: call [004010ECh] ; __vbaI2I4
  loc_004159E4: push eax
  loc_004159E5: call [004010CCh] ; __vbaFileClose
  loc_004159EB: mov var_4, 00000027h
  loc_004159F2: call [004010A0h] ; rtcDoEvents
  loc_004159F8: mov var_4, 00000028h
  loc_004159FF: mov var_70, 80020004h
  loc_00415A06: mov var_78, 0000000Ah
  loc_00415A0D: lea edx, var_78
  loc_00415A10: push edx
  loc_00415A11: call [00401164h] ; rtcFreeFile
  loc_00415A17: movsx eax, ax
  loc_00415A1A: mov var_30, eax
  loc_00415A1D: lea ecx, var_78
  loc_00415A20: call [00401020h] ; __vbaFreeVar
  loc_00415A26: mov var_4, 00000029h
  loc_00415A2D: mov edx, 0040704Ch ; "MovesMajor"
  loc_00415A32: lea ecx, var_4C
  loc_00415A35: call [00401178h] ; __vbaStrCopy
  loc_00415A3B: lea ecx, var_50
  loc_00415A3E: push ecx
  loc_00415A3F: lea edx, var_4C
  loc_00415A42: push edx
  loc_00415A43: mov eax, var_48
  loc_00415A46: mov ecx, [eax]
  loc_00415A48: mov edx, var_48
  loc_00415A4B: push edx
  loc_00415A4C: call [ecx+0000002Ch]
  loc_00415A4F: fnclex
  loc_00415A51: mov var_1B8, eax
  loc_00415A57: cmp var_1B8, 00000000h
  loc_00415A5E: jge 00415A80h
  loc_00415A60: push 0000002Ch
  loc_00415A62: push 00405B8Ch
  loc_00415A67: mov eax, var_48
  loc_00415A6A: push eax
  loc_00415A6B: mov ecx, var_1B8
  loc_00415A71: push ecx
  loc_00415A72: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00415A78: mov var_258, eax
  loc_00415A7E: jmp 00415A8Ah
  loc_00415A80: mov var_258, 00000000h
  loc_00415A8A: mov edx, var_50
  loc_00415A8D: push edx
  loc_00415A8E: push 00407078h ; "Y.PMV"
  loc_00415A93: call [00401050h] ; __vbaStrCat
  loc_00415A99: mov edx, eax
  loc_00415A9B: lea ecx, var_54
  loc_00415A9E: call [004011D0h] ; __vbaStrMove
  loc_00415AA4: push eax
  loc_00415AA5: mov ecx, var_30
  loc_00415AA8: call [004010ECh] ; __vbaI2I4
  loc_00415AAE: push eax
  loc_00415AAF: push FFFFFFFFh
  loc_00415AB1: push 00004101h
  loc_00415AB6: call [0040115Ch] ; __vbaFileOpen
  loc_00415ABC: lea eax, var_54
  loc_00415ABF: push eax
  loc_00415AC0: lea ecx, var_50
  loc_00415AC3: push ecx
  loc_00415AC4: lea edx, var_4C
  loc_00415AC7: push edx
  loc_00415AC8: push 00000003h
  loc_00415ACA: call [00401180h] ; __vbaFreeStrList
  loc_00415AD0: add esp, 00000010h
  loc_00415AD3: mov var_4, 0000002Ah
  loc_00415ADA: mov eax, Me
  loc_00415ADD: mov ecx, [eax+00000054h]
  loc_00415AE0: sub ecx, 00000001h
  loc_00415AE3: jo 00418DF3h
  loc_00415AE9: call [004010ECh] ; __vbaI2I4
  loc_00415AEF: mov var_1DC, ax
  loc_00415AF6: mov var_1D8, 0001h
  loc_00415AFF: mov var_24, 0000h
  loc_00415B05: jmp 00415B1Ch
  loc_00415B07: mov cx, var_24
  loc_00415B0B: add cx, var_1D8
  loc_00415B12: jo 00418DF3h
  loc_00415B18: mov var_24, cx
  loc_00415B1C: mov dx, var_24
  loc_00415B20: cmp dx, var_1DC
  loc_00415B27: jg 00415BE5h
  loc_00415B2D: mov var_4, 0000002Bh
  loc_00415B34: mov ecx, var_30
  loc_00415B37: call [004010ECh] ; __vbaI2I4
  loc_00415B3D: push eax
  loc_00415B3E: lea eax, var_2C
  loc_00415B41: push eax
  loc_00415B42: call [00401028h] ; __vbaLineInputStr
  loc_00415B48: mov var_4, 0000002Ch
  loc_00415B4F: mov ecx, Me
  loc_00415B52: cmp [ecx+00000044h], 00000000h
  loc_00415B56: jz 00415BB1h
  loc_00415B58: mov edx, Me
  loc_00415B5B: mov eax, [edx+00000044h]
  loc_00415B5E: cmp [eax], 0001h
  loc_00415B62: jnz 00415BB1h
  loc_00415B64: movsx ecx, var_24
  loc_00415B68: mov edx, Me
  loc_00415B6B: mov eax, [edx+00000044h]
  loc_00415B6E: sub ecx, [eax+00000014h]
  loc_00415B71: mov var_1B8, ecx
  loc_00415B77: mov ecx, Me
  loc_00415B7A: mov edx, [ecx+00000044h]
  loc_00415B7D: mov eax, var_1B8
  loc_00415B83: cmp eax, [edx+00000010h]
  loc_00415B86: jae 00415B94h
  loc_00415B88: mov var_25C, 00000000h
  loc_00415B92: jmp 00415BA0h
  loc_00415B94: call [004010D8h] ; __vbaGenerateBoundsError
  loc_00415B9A: mov var_25C, eax
  loc_00415BA0: mov ecx, var_1B8
  loc_00415BA6: shl ecx, 02h
  loc_00415BA9: mov var_260, ecx
  loc_00415BAF: jmp 00415BBDh
  loc_00415BB1: call [004010D8h] ; __vbaGenerateBoundsError
  loc_00415BB7: mov var_260, eax
  loc_00415BBD: mov edx, var_2C
  loc_00415BC0: push edx
  loc_00415BC1: call [0040117Ch] ; __vbaI4Str
  loc_00415BC7: mov ecx, Me
  loc_00415BCA: mov edx, [ecx+00000044h]
  loc_00415BCD: mov ecx, [edx+0000000Ch]
  loc_00415BD0: mov edx, var_260
  loc_00415BD6: mov [ecx+edx], eax
  loc_00415BD9: mov var_4, 0000002Dh
  loc_00415BE0: jmp 00415B07h
  loc_00415BE5: mov var_4, 0000002Eh
  loc_00415BEC: mov ecx, var_30
  loc_00415BEF: call [004010ECh] ; __vbaI2I4
  loc_00415BF5: push eax
  loc_00415BF6: call [004010CCh] ; __vbaFileClose
  loc_00415BFC: mov var_4, 0000002Fh
  loc_00415C03: call [004010A0h] ; rtcDoEvents
  loc_00415C09: mov var_4, 00000030h
  loc_00415C10: mov var_70, 80020004h
  loc_00415C17: mov var_78, 0000000Ah
  loc_00415C1E: lea eax, var_78
  loc_00415C21: push eax
  loc_00415C22: call [00401164h] ; rtcFreeFile
  loc_00415C28: movsx ecx, ax
  loc_00415C2B: mov var_30, ecx
  loc_00415C2E: lea ecx, var_78
  loc_00415C31: call [00401020h] ; __vbaFreeVar
  loc_00415C37: mov var_4, 00000031h
  loc_00415C3E: mov edx, 00407088h ; "DeviceIDMajor"
  loc_00415C43: lea ecx, var_4C
  loc_00415C46: call [00401178h] ; __vbaStrCopy
  loc_00415C4C: lea edx, var_50
  loc_00415C4F: push edx
  loc_00415C50: lea eax, var_4C
  loc_00415C53: push eax
  loc_00415C54: mov ecx, var_48
  loc_00415C57: mov edx, [ecx]
  loc_00415C59: mov eax, var_48
  loc_00415C5C: push eax
  loc_00415C5D: call [edx+0000002Ch]
  loc_00415C60: fnclex
  loc_00415C62: mov var_1B8, eax
  loc_00415C68: cmp var_1B8, 00000000h
  loc_00415C6F: jge 00415C91h
  loc_00415C71: push 0000002Ch
  loc_00415C73: push 00405B8Ch
  loc_00415C78: mov ecx, var_48
  loc_00415C7B: push ecx
  loc_00415C7C: mov edx, var_1B8
  loc_00415C82: push edx
  loc_00415C83: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00415C89: mov var_264, eax
  loc_00415C8F: jmp 00415C9Bh
  loc_00415C91: mov var_264, 00000000h
  loc_00415C9B: mov eax, var_50
  loc_00415C9E: push eax
  loc_00415C9F: mov ecx, var_30
  loc_00415CA2: call [004010ECh] ; __vbaI2I4
  loc_00415CA8: push eax
  loc_00415CA9: push FFFFFFFFh
  loc_00415CAB: push 00004101h
  loc_00415CB0: call [0040115Ch] ; __vbaFileOpen
  loc_00415CB6: lea ecx, var_50
  loc_00415CB9: push ecx
  loc_00415CBA: lea edx, var_4C
  loc_00415CBD: push edx
  loc_00415CBE: push 00000002h
  loc_00415CC0: call [00401180h] ; __vbaFreeStrList
  loc_00415CC6: add esp, 0000000Ch
  loc_00415CC9: mov var_4, 00000032h
  loc_00415CD0: mov eax, Me
  loc_00415CD3: mov ecx, [eax+00000054h]
  loc_00415CD6: sub ecx, 00000001h
  loc_00415CD9: jo 00418DF3h
  loc_00415CDF: call [004010ECh] ; __vbaI2I4
  loc_00415CE5: mov var_1E4, ax
  loc_00415CEC: mov var_1E0, 0001h
  loc_00415CF5: mov var_24, 0000h
  loc_00415CFB: jmp 00415D12h
  loc_00415CFD: mov cx, var_24
  loc_00415D01: add cx, var_1E0
  loc_00415D08: jo 00418DF3h
  loc_00415D0E: mov var_24, cx
  loc_00415D12: mov dx, var_24
  loc_00415D16: cmp dx, var_1E4
  loc_00415D1D: jg 00415DD7h
  loc_00415D23: mov var_4, 00000033h
  loc_00415D2A: mov ecx, var_30
  loc_00415D2D: call [004010ECh] ; __vbaI2I4
  loc_00415D33: push eax
  loc_00415D34: lea eax, var_2C
  loc_00415D37: push eax
  loc_00415D38: call [00401028h] ; __vbaLineInputStr
  loc_00415D3E: mov var_4, 00000034h
  loc_00415D45: mov ecx, Me
  loc_00415D48: cmp [ecx+0000004Ch], 00000000h
  loc_00415D4C: jz 00415DA7h
  loc_00415D4E: mov edx, Me
  loc_00415D51: mov eax, [edx+0000004Ch]
  loc_00415D54: cmp [eax], 0001h
  loc_00415D58: jnz 00415DA7h
  loc_00415D5A: movsx ecx, var_24
  loc_00415D5E: mov edx, Me
  loc_00415D61: mov eax, [edx+0000004Ch]
  loc_00415D64: sub ecx, [eax+00000014h]
  loc_00415D67: mov var_1B8, ecx
  loc_00415D6D: mov ecx, Me
  loc_00415D70: mov edx, [ecx+0000004Ch]
  loc_00415D73: mov eax, var_1B8
  loc_00415D79: cmp eax, [edx+00000010h]
  loc_00415D7C: jae 00415D8Ah
  loc_00415D7E: mov var_268, 00000000h
  loc_00415D88: jmp 00415D96h
  loc_00415D8A: call [004010D8h] ; __vbaGenerateBoundsError
  loc_00415D90: mov var_268, eax
  loc_00415D96: mov ecx, var_1B8
  loc_00415D9C: shl ecx, 02h
  loc_00415D9F: mov var_26C, ecx
  loc_00415DA5: jmp 00415DB3h
  loc_00415DA7: call [004010D8h] ; __vbaGenerateBoundsError
  loc_00415DAD: mov var_26C, eax
  loc_00415DB3: mov edx, var_2C
  loc_00415DB6: mov eax, Me
  loc_00415DB9: mov ecx, [eax+0000004Ch]
  loc_00415DBC: mov ecx, [ecx+0000000Ch]
  loc_00415DBF: add ecx, var_26C
  loc_00415DC5: call [00401178h] ; __vbaStrCopy
  loc_00415DCB: mov var_4, 00000035h
  loc_00415DD2: jmp 00415CFDh
  loc_00415DD7: mov var_4, 00000036h
  loc_00415DDE: mov ecx, var_30
  loc_00415DE1: call [004010ECh] ; __vbaI2I4
  loc_00415DE7: push eax
  loc_00415DE8: call [004010CCh] ; __vbaFileClose
  loc_00415DEE: mov var_4, 00000037h
  loc_00415DF5: call [004010A0h] ; rtcDoEvents
  loc_00415DFB: mov var_4, 00000038h
  loc_00415E02: mov edx, Me
  loc_00415E05: cmp [edx+00000058h], 00000001h
  loc_00415E09: jle 00416498h
  loc_00415E0F: mov var_4, 00000039h
  loc_00415E16: push 00000000h
  loc_00415E18: mov eax, Me
  loc_00415E1B: mov ecx, [eax+00000058h]
  loc_00415E1E: sub ecx, 00000001h
  loc_00415E21: jo 00418DF3h
  loc_00415E27: push ecx
  loc_00415E28: push 00000001h
  loc_00415E2A: push 00000003h
  loc_00415E2C: mov edx, Me
  loc_00415E2F: add edx, 00000040h
  loc_00415E32: push edx
  loc_00415E33: push 00000004h
  loc_00415E35: push 00000080h
  loc_00415E3A: call [00401108h] ; __vbaRedim
  loc_00415E40: add esp, 0000001Ch
  loc_00415E43: mov var_4, 0000003Ah
  loc_00415E4A: push 00000000h
  loc_00415E4C: mov eax, Me
  loc_00415E4F: mov ecx, [eax+00000058h]
  loc_00415E52: sub ecx, 00000001h
  loc_00415E55: jo 00418DF3h
  loc_00415E5B: push ecx
  loc_00415E5C: push 00000001h
  loc_00415E5E: push 00000003h
  loc_00415E60: mov edx, Me
  loc_00415E63: add edx, 00000048h
  loc_00415E66: push edx
  loc_00415E67: push 00000004h
  loc_00415E69: push 00000080h
  loc_00415E6E: call [00401108h] ; __vbaRedim
  loc_00415E74: add esp, 0000001Ch
  loc_00415E77: mov var_4, 0000003Bh
  loc_00415E7E: push 00000000h
  loc_00415E80: mov eax, Me
  loc_00415E83: mov ecx, [eax+00000058h]
  loc_00415E86: sub ecx, 00000001h
  loc_00415E89: jo 00418DF3h
  loc_00415E8F: push ecx
  loc_00415E90: push 00000001h
  loc_00415E92: push 00000008h
  loc_00415E94: mov edx, Me
  loc_00415E97: add edx, 00000050h
  loc_00415E9A: push edx
  loc_00415E9B: push 00000004h
  loc_00415E9D: push 00000180h
  loc_00415EA2: call [00401108h] ; __vbaRedim
  loc_00415EA8: add esp, 0000001Ch
  loc_00415EAB: mov var_4, 0000003Ch
  loc_00415EB2: mov var_70, 80020004h
  loc_00415EB9: mov var_78, 0000000Ah
  loc_00415EC0: lea eax, var_78
  loc_00415EC3: push eax
  loc_00415EC4: call [00401164h] ; rtcFreeFile
  loc_00415ECA: movsx ecx, ax
  loc_00415ECD: mov var_30, ecx
  loc_00415ED0: lea ecx, var_78
  loc_00415ED3: call [00401020h] ; __vbaFreeVar
  loc_00415ED9: mov var_4, 0000003Dh
  loc_00415EE0: mov edx, 00406EC4h ; "MovesMinor"
  loc_00415EE5: lea ecx, var_4C
  loc_00415EE8: call [00401178h] ; __vbaStrCopy
  loc_00415EEE: lea edx, var_50
  loc_00415EF1: push edx
  loc_00415EF2: lea eax, var_4C
  loc_00415EF5: push eax
  loc_00415EF6: mov ecx, var_48
  loc_00415EF9: mov edx, [ecx]
  loc_00415EFB: mov eax, var_48
  loc_00415EFE: push eax
  loc_00415EFF: call [edx+0000002Ch]
  loc_00415F02: fnclex
  loc_00415F04: mov var_1B8, eax
  loc_00415F0A: cmp var_1B8, 00000000h
  loc_00415F11: jge 00415F33h
  loc_00415F13: push 0000002Ch
  loc_00415F15: push 00405B8Ch
  loc_00415F1A: mov ecx, var_48
  loc_00415F1D: push ecx
  loc_00415F1E: mov edx, var_1B8
  loc_00415F24: push edx
  loc_00415F25: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00415F2B: mov var_270, eax
  loc_00415F31: jmp 00415F3Dh
  loc_00415F33: mov var_270, 00000000h
  loc_00415F3D: mov eax, var_50
  loc_00415F40: push eax
  loc_00415F41: push 00407068h ; "X.PMV"
  loc_00415F46: call [00401050h] ; __vbaStrCat
  loc_00415F4C: mov edx, eax
  loc_00415F4E: lea ecx, var_54
  loc_00415F51: call [004011D0h] ; __vbaStrMove
  loc_00415F57: push eax
  loc_00415F58: mov ecx, var_30
  loc_00415F5B: call [004010ECh] ; __vbaI2I4
  loc_00415F61: push eax
  loc_00415F62: push FFFFFFFFh
  loc_00415F64: push 00004101h
  loc_00415F69: call [0040115Ch] ; __vbaFileOpen
  loc_00415F6F: lea ecx, var_54
  loc_00415F72: push ecx
  loc_00415F73: lea edx, var_50
  loc_00415F76: push edx
  loc_00415F77: lea eax, var_4C
  loc_00415F7A: push eax
  loc_00415F7B: push 00000003h
  loc_00415F7D: call [00401180h] ; __vbaFreeStrList
  loc_00415F83: add esp, 00000010h
  loc_00415F86: mov var_4, 0000003Eh
  loc_00415F8D: mov ecx, Me
  loc_00415F90: mov ecx, [ecx+00000058h]
  loc_00415F93: sub ecx, 00000001h
  loc_00415F96: jo 00418DF3h
  loc_00415F9C: call [004010ECh] ; __vbaI2I4
  loc_00415FA2: mov var_1EC, ax
  loc_00415FA9: mov var_1E8, 0001h
  loc_00415FB2: mov var_24, 0000h
  loc_00415FB8: jmp 00415FCFh
  loc_00415FBA: mov dx, var_24
  loc_00415FBE: add dx, var_1E8
  loc_00415FC5: jo 00418DF3h
  loc_00415FCB: mov var_24, dx
  loc_00415FCF: mov ax, var_24
  loc_00415FD3: cmp ax, var_1EC
  loc_00415FDA: jg 00416098h
  loc_00415FE0: mov var_4, 0000003Fh
  loc_00415FE7: mov ecx, var_30
  loc_00415FEA: call [004010ECh] ; __vbaI2I4
  loc_00415FF0: push eax
  loc_00415FF1: lea ecx, var_2C
  loc_00415FF4: push ecx
  loc_00415FF5: call [00401028h] ; __vbaLineInputStr
  loc_00415FFB: mov var_4, 00000040h
  loc_00416002: mov edx, Me
  loc_00416005: cmp [edx+00000040h], 00000000h
  loc_00416009: jz 00416064h
  loc_0041600B: mov eax, Me
  loc_0041600E: mov ecx, [eax+00000040h]
  loc_00416011: cmp [ecx], 0001h
  loc_00416015: jnz 00416064h
  loc_00416017: movsx edx, var_24
  loc_0041601B: mov eax, Me
  loc_0041601E: mov ecx, [eax+00000040h]
  loc_00416021: sub edx, [ecx+00000014h]
  loc_00416024: mov var_1B8, edx
  loc_0041602A: mov edx, Me
  loc_0041602D: mov eax, [edx+00000040h]
  loc_00416030: mov ecx, var_1B8
  loc_00416036: cmp ecx, [eax+00000010h]
  loc_00416039: jae 00416047h
  loc_0041603B: mov var_274, 00000000h
  loc_00416045: jmp 00416053h
  loc_00416047: call [004010D8h] ; __vbaGenerateBoundsError
  loc_0041604D: mov var_274, eax
  loc_00416053: mov edx, var_1B8
  loc_00416059: shl edx, 02h
  loc_0041605C: mov var_278, edx
  loc_00416062: jmp 00416070h
  loc_00416064: call [004010D8h] ; __vbaGenerateBoundsError
  loc_0041606A: mov var_278, eax
  loc_00416070: mov eax, var_2C
  loc_00416073: push eax
  loc_00416074: call [0040117Ch] ; __vbaI4Str
  loc_0041607A: mov ecx, Me
  loc_0041607D: mov edx, [ecx+00000040h]
  loc_00416080: mov ecx, [edx+0000000Ch]
  loc_00416083: mov edx, var_278
  loc_00416089: mov [ecx+edx], eax
  loc_0041608C: mov var_4, 00000041h
  loc_00416093: jmp 00415FBAh
  loc_00416098: mov var_4, 00000042h
  loc_0041609F: mov ecx, var_30
  loc_004160A2: call [004010ECh] ; __vbaI2I4
  loc_004160A8: push eax
  loc_004160A9: call [004010CCh] ; __vbaFileClose
  loc_004160AF: mov var_4, 00000043h
  loc_004160B6: mov var_70, 80020004h
  loc_004160BD: mov var_78, 0000000Ah
  loc_004160C4: lea eax, var_78
  loc_004160C7: push eax
  loc_004160C8: call [00401164h] ; rtcFreeFile
  loc_004160CE: movsx ecx, ax
  loc_004160D1: mov var_30, ecx
  loc_004160D4: lea ecx, var_78
  loc_004160D7: call [00401020h] ; __vbaFreeVar
  loc_004160DD: mov var_4, 00000044h
  loc_004160E4: mov edx, 00406EC4h ; "MovesMinor"
  loc_004160E9: lea ecx, var_4C
  loc_004160EC: call [00401178h] ; __vbaStrCopy
  loc_004160F2: lea edx, var_50
  loc_004160F5: push edx
  loc_004160F6: lea eax, var_4C
  loc_004160F9: push eax
  loc_004160FA: mov ecx, var_48
  loc_004160FD: mov edx, [ecx]
  loc_004160FF: mov eax, var_48
  loc_00416102: push eax
  loc_00416103: call [edx+0000002Ch]
  loc_00416106: fnclex
  loc_00416108: mov var_1B8, eax
  loc_0041610E: cmp var_1B8, 00000000h
  loc_00416115: jge 00416137h
  loc_00416117: push 0000002Ch
  loc_00416119: push 00405B8Ch
  loc_0041611E: mov ecx, var_48
  loc_00416121: push ecx
  loc_00416122: mov edx, var_1B8
  loc_00416128: push edx
  loc_00416129: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041612F: mov var_27C, eax
  loc_00416135: jmp 00416141h
  loc_00416137: mov var_27C, 00000000h
  loc_00416141: mov eax, var_50
  loc_00416144: push eax
  loc_00416145: push 00407078h ; "Y.PMV"
  loc_0041614A: call [00401050h] ; __vbaStrCat
  loc_00416150: mov edx, eax
  loc_00416152: lea ecx, var_54
  loc_00416155: call [004011D0h] ; __vbaStrMove
  loc_0041615B: push eax
  loc_0041615C: mov ecx, var_30
  loc_0041615F: call [004010ECh] ; __vbaI2I4
  loc_00416165: push eax
  loc_00416166: push FFFFFFFFh
  loc_00416168: push 00004101h
  loc_0041616D: call [0040115Ch] ; __vbaFileOpen
  loc_00416173: lea ecx, var_54
  loc_00416176: push ecx
  loc_00416177: lea edx, var_50
  loc_0041617A: push edx
  loc_0041617B: lea eax, var_4C
  loc_0041617E: push eax
  loc_0041617F: push 00000003h
  loc_00416181: call [00401180h] ; __vbaFreeStrList
  loc_00416187: add esp, 00000010h
  loc_0041618A: mov var_4, 00000045h
  loc_00416191: mov ecx, Me
  loc_00416194: mov ecx, [ecx+00000058h]
  loc_00416197: sub ecx, 00000001h
  loc_0041619A: jo 00418DF3h
  loc_004161A0: call [004010ECh] ; __vbaI2I4
  loc_004161A6: mov var_1F4, ax
  loc_004161AD: mov var_1F0, 0001h
  loc_004161B6: mov var_24, 0000h
  loc_004161BC: jmp 004161D3h
  loc_004161BE: mov dx, var_24
  loc_004161C2: add dx, var_1F0
  loc_004161C9: jo 00418DF3h
  loc_004161CF: mov var_24, dx
  loc_004161D3: mov ax, var_24
  loc_004161D7: cmp ax, var_1F4
  loc_004161DE: jg 0041629Ch
  loc_004161E4: mov var_4, 00000046h
  loc_004161EB: mov ecx, var_30
  loc_004161EE: call [004010ECh] ; __vbaI2I4
  loc_004161F4: push eax
  loc_004161F5: lea ecx, var_2C
  loc_004161F8: push ecx
  loc_004161F9: call [00401028h] ; __vbaLineInputStr
  loc_004161FF: mov var_4, 00000047h
  loc_00416206: mov edx, Me
  loc_00416209: cmp [edx+00000048h], 00000000h
  loc_0041620D: jz 00416268h
  loc_0041620F: mov eax, Me
  loc_00416212: mov ecx, [eax+00000048h]
  loc_00416215: cmp [ecx], 0001h
  loc_00416219: jnz 00416268h
  loc_0041621B: movsx edx, var_24
  loc_0041621F: mov eax, Me
  loc_00416222: mov ecx, [eax+00000048h]
  loc_00416225: sub edx, [ecx+00000014h]
  loc_00416228: mov var_1B8, edx
  loc_0041622E: mov edx, Me
  loc_00416231: mov eax, [edx+00000048h]
  loc_00416234: mov ecx, var_1B8
  loc_0041623A: cmp ecx, [eax+00000010h]
  loc_0041623D: jae 0041624Bh
  loc_0041623F: mov var_280, 00000000h
  loc_00416249: jmp 00416257h
  loc_0041624B: call [004010D8h] ; __vbaGenerateBoundsError
  loc_00416251: mov var_280, eax
  loc_00416257: mov edx, var_1B8
  loc_0041625D: shl edx, 02h
  loc_00416260: mov var_284, edx
  loc_00416266: jmp 00416274h
  loc_00416268: call [004010D8h] ; __vbaGenerateBoundsError
  loc_0041626E: mov var_284, eax
  loc_00416274: mov eax, var_2C
  loc_00416277: push eax
  loc_00416278: call [0040117Ch] ; __vbaI4Str
  loc_0041627E: mov ecx, Me
  loc_00416281: mov edx, [ecx+00000048h]
  loc_00416284: mov ecx, [edx+0000000Ch]
  loc_00416287: mov edx, var_284
  loc_0041628D: mov [ecx+edx], eax
  loc_00416290: mov var_4, 00000048h
  loc_00416297: jmp 004161BEh
  loc_0041629C: mov var_4, 00000049h
  loc_004162A3: mov ecx, var_30
  loc_004162A6: call [004010ECh] ; __vbaI2I4
  loc_004162AC: push eax
  loc_004162AD: call [004010CCh] ; __vbaFileClose
  loc_004162B3: mov var_4, 0000004Ah
  loc_004162BA: mov var_70, 80020004h
  loc_004162C1: mov var_78, 0000000Ah
  loc_004162C8: lea eax, var_78
  loc_004162CB: push eax
  loc_004162CC: call [00401164h] ; rtcFreeFile
  loc_004162D2: movsx ecx, ax
  loc_004162D5: mov var_30, ecx
  loc_004162D8: lea ecx, var_78
  loc_004162DB: call [00401020h] ; __vbaFreeVar
  loc_004162E1: mov var_4, 0000004Bh
  loc_004162E8: mov edx, 004070A8h ; "DeviceIDMinor"
  loc_004162ED: lea ecx, var_4C
  loc_004162F0: call [00401178h] ; __vbaStrCopy
  loc_004162F6: lea edx, var_50
  loc_004162F9: push edx
  loc_004162FA: lea eax, var_4C
  loc_004162FD: push eax
  loc_004162FE: mov ecx, var_48
  loc_00416301: mov edx, [ecx]
  loc_00416303: mov eax, var_48
  loc_00416306: push eax
  loc_00416307: call [edx+0000002Ch]
  loc_0041630A: fnclex
  loc_0041630C: mov var_1B8, eax
  loc_00416312: cmp var_1B8, 00000000h
  loc_00416319: jge 0041633Bh
  loc_0041631B: push 0000002Ch
  loc_0041631D: push 00405B8Ch
  loc_00416322: mov ecx, var_48
  loc_00416325: push ecx
  loc_00416326: mov edx, var_1B8
  loc_0041632C: push edx
  loc_0041632D: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00416333: mov var_288, eax
  loc_00416339: jmp 00416345h
  loc_0041633B: mov var_288, 00000000h
  loc_00416345: mov eax, var_50
  loc_00416348: push eax
  loc_00416349: mov ecx, var_30
  loc_0041634C: call [004010ECh] ; __vbaI2I4
  loc_00416352: push eax
  loc_00416353: push FFFFFFFFh
  loc_00416355: push 00004101h
  loc_0041635A: call [0040115Ch] ; __vbaFileOpen
  loc_00416360: lea ecx, var_50
  loc_00416363: push ecx
  loc_00416364: lea edx, var_4C
  loc_00416367: push edx
  loc_00416368: push 00000002h
  loc_0041636A: call [00401180h] ; __vbaFreeStrList
  loc_00416370: add esp, 0000000Ch
  loc_00416373: mov var_4, 0000004Ch
  loc_0041637A: mov eax, Me
  loc_0041637D: mov ecx, [eax+00000058h]
  loc_00416380: sub ecx, 00000001h
  loc_00416383: jo 00418DF3h
  loc_00416389: call [004010ECh] ; __vbaI2I4
  loc_0041638F: mov var_1FC, ax
  loc_00416396: mov var_1F8, 0001h
  loc_0041639F: mov var_24, 0000h
  loc_004163A5: jmp 004163BCh
  loc_004163A7: mov cx, var_24
  loc_004163AB: add cx, var_1F8
  loc_004163B2: jo 00418DF3h
  loc_004163B8: mov var_24, cx
  loc_004163BC: mov dx, var_24
  loc_004163C0: cmp dx, var_1FC
  loc_004163C7: jg 00416481h
  loc_004163CD: mov var_4, 0000004Dh
  loc_004163D4: mov ecx, var_30
  loc_004163D7: call [004010ECh] ; __vbaI2I4
  loc_004163DD: push eax
  loc_004163DE: lea eax, var_2C
  loc_004163E1: push eax
  loc_004163E2: call [00401028h] ; __vbaLineInputStr
  loc_004163E8: mov var_4, 0000004Eh
  loc_004163EF: mov ecx, Me
  loc_004163F2: cmp [ecx+00000050h], 00000000h
  loc_004163F6: jz 00416451h
  loc_004163F8: mov edx, Me
  loc_004163FB: mov eax, [edx+00000050h]
  loc_004163FE: cmp [eax], 0001h
  loc_00416402: jnz 00416451h
  loc_00416404: movsx ecx, var_24
  loc_00416408: mov edx, Me
  loc_0041640B: mov eax, [edx+00000050h]
  loc_0041640E: sub ecx, [eax+00000014h]
  loc_00416411: mov var_1B8, ecx
  loc_00416417: mov ecx, Me
  loc_0041641A: mov edx, [ecx+00000050h]
  loc_0041641D: mov eax, var_1B8
  loc_00416423: cmp eax, [edx+00000010h]
  loc_00416426: jae 00416434h
  loc_00416428: mov var_28C, 00000000h
  loc_00416432: jmp 00416440h
  loc_00416434: call [004010D8h] ; __vbaGenerateBoundsError
  loc_0041643A: mov var_28C, eax
  loc_00416440: mov ecx, var_1B8
  loc_00416446: shl ecx, 02h
  loc_00416449: mov var_290, ecx
  loc_0041644F: jmp 0041645Dh
  loc_00416451: call [004010D8h] ; __vbaGenerateBoundsError
  loc_00416457: mov var_290, eax
  loc_0041645D: mov edx, var_2C
  loc_00416460: mov eax, Me
  loc_00416463: mov ecx, [eax+00000050h]
  loc_00416466: mov ecx, [ecx+0000000Ch]
  loc_00416469: add ecx, var_290
  loc_0041646F: call [00401178h] ; __vbaStrCopy
  loc_00416475: mov var_4, 0000004Fh
  loc_0041647C: jmp 004163A7h
  loc_00416481: mov var_4, 00000050h
  loc_00416488: mov ecx, var_30
  loc_0041648B: call [004010ECh] ; __vbaI2I4
  loc_00416491: push eax
  loc_00416492: call [004010CCh] ; __vbaFileClose
  loc_00416498: mov var_4, 00000052h
  loc_0041649F: mov edx, Me
  loc_004164A2: mov eax, [edx]
  loc_004164A4: mov ecx, Me
  loc_004164A7: push ecx
  loc_004164A8: call [eax+00000394h]
  loc_004164AE: push eax
  loc_004164AF: lea edx, var_64
  loc_004164B2: push edx
  loc_004164B3: call [00401080h] ; __vbaObjSet
  loc_004164B9: mov var_1B8, eax
  loc_004164BF: push 00000000h
  loc_004164C1: mov eax, var_1B8
  loc_004164C7: mov ecx, [eax]
  loc_004164C9: mov edx, var_1B8
  loc_004164CF: push edx
  loc_004164D0: call [ecx+0000005Ch]
  loc_004164D3: fnclex
  loc_004164D5: mov var_1BC, eax
  loc_004164DB: cmp var_1BC, 00000000h
  loc_004164E2: jge 00416507h
  loc_004164E4: push 0000005Ch
  loc_004164E6: push 004056F4h
  loc_004164EB: mov eax, var_1B8
  loc_004164F1: push eax
  loc_004164F2: mov ecx, var_1BC
  loc_004164F8: push ecx
  loc_004164F9: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004164FF: mov var_294, eax
  loc_00416505: jmp 00416511h
  loc_00416507: mov var_294, 00000000h
  loc_00416511: lea ecx, var_64
  loc_00416514: call [004011F0h] ; __vbaFreeObj
  loc_0041651A: mov var_4, 00000053h
  loc_00416521: mov edx, Me
  loc_00416524: mov eax, [edx]
  loc_00416526: mov ecx, Me
  loc_00416529: push ecx
  loc_0041652A: call [eax+0000039Ch]
  loc_00416530: push eax
  loc_00416531: lea edx, var_64
  loc_00416534: push edx
  loc_00416535: call [00401080h] ; __vbaObjSet
  loc_0041653B: mov var_1B8, eax
  loc_00416541: push 004070C8h ; "Initializing Electroglass"
  loc_00416546: mov eax, var_1B8
  loc_0041654C: mov ecx, [eax]
  loc_0041654E: mov edx, var_1B8
  loc_00416554: push edx
  loc_00416555: call [ecx+00000054h]
  loc_00416558: fnclex
  loc_0041655A: mov var_1BC, eax
  loc_00416560: cmp var_1BC, 00000000h
  loc_00416567: jge 0041658Ch
  loc_00416569: push 00000054h
  loc_0041656B: push 0040575Ch
  loc_00416570: mov eax, var_1B8
  loc_00416576: push eax
  loc_00416577: mov ecx, var_1BC
  loc_0041657D: push ecx
  loc_0041657E: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00416584: mov var_298, eax
  loc_0041658A: jmp 00416596h
  loc_0041658C: mov var_298, 00000000h
  loc_00416596: lea ecx, var_64
  loc_00416599: call [004011F0h] ; __vbaFreeObj
  loc_0041659F: mov var_4, 00000054h
  loc_004165A6: mov edx, Me
  loc_004165A9: mov eax, [edx]
  loc_004165AB: mov ecx, Me
  loc_004165AE: push ecx
  loc_004165AF: call [eax+00000394h]
  loc_004165B5: push eax
  loc_004165B6: lea edx, var_64
  loc_004165B9: push edx
  loc_004165BA: call [00401080h] ; __vbaObjSet
  loc_004165C0: mov var_1B8, eax
  loc_004165C6: push FFFFFFFFh
  loc_004165C8: mov eax, var_1B8
  loc_004165CE: mov ecx, [eax]
  loc_004165D0: mov edx, var_1B8
  loc_004165D6: push edx
  loc_004165D7: call [ecx+0000005Ch]
  loc_004165DA: fnclex
  loc_004165DC: mov var_1BC, eax
  loc_004165E2: cmp var_1BC, 00000000h
  loc_004165E9: jge 0041660Eh
  loc_004165EB: push 0000005Ch
  loc_004165ED: push 004056F4h
  loc_004165F2: mov eax, var_1B8
  loc_004165F8: push eax
  loc_004165F9: mov ecx, var_1BC
  loc_004165FF: push ecx
  loc_00416600: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00416606: mov var_29C, eax
  loc_0041660C: jmp 00416618h
  loc_0041660E: mov var_29C, 00000000h
  loc_00416618: lea ecx, var_64
  loc_0041661B: call [004011F0h] ; __vbaFreeObj
  loc_00416621: mov var_4, 00000055h
  loc_00416628: mov edx, Me
  loc_0041662B: movsx eax, [edx+0000005Ch]
  loc_0041662F: test eax, eax
  loc_00416631: jnz 00417A16h
  loc_00416637: mov var_4, 00000056h
  loc_0041663E: lea ecx, var_78
  loc_00416641: push ecx
  loc_00416642: mov edx, Me
  loc_00416645: mov eax, [edx]
  loc_00416647: mov ecx, Me
  loc_0041664A: push ecx
  loc_0041664B: call [eax+00000724h]
  loc_00416651: lea edx, var_78
  loc_00416654: lea ecx, var_40
  loc_00416657: call [00401014h] ; __vbaVarMove
  loc_0041665D: mov var_4, 00000057h
  loc_00416664: mov var_120, 00000000h
  loc_0041666E: mov var_128, 00008002h
  loc_00416678: lea edx, var_40
  loc_0041667B: push edx
  loc_0041667C: lea eax, var_128
  loc_00416682: push eax
  loc_00416683: call [00401198h] ; __vbaVarTstNe
  loc_00416689: movsx ecx, ax
  loc_0041668C: test ecx, ecx
  loc_0041668E: jz 004167FDh
  loc_00416694: mov var_4, 00000058h
  loc_0041669B: mov var_A0, 80020004h
  loc_004166A5: mov var_A8, 0000000Ah
  loc_004166AF: mov var_90, 80020004h
  loc_004166B9: mov var_98, 0000000Ah
  loc_004166C3: mov var_120, 004050E8h ; "IMT LampElectrical Probing"
  loc_004166CD: mov var_128, 00000008h
  loc_004166D7: lea edx, var_128
  loc_004166DD: lea ecx, var_88
  loc_004166E3: call [004011B4h] ; __vbaVarDup
  loc_004166E9: push 00407100h ; "Configure HPIB Failed"
  loc_004166EE: push 004054D8h ; vbCrLf
  loc_004166F3: call [00401050h] ; __vbaStrCat
  loc_004166F9: mov edx, eax
  loc_004166FB: lea ecx, var_4C
  loc_004166FE: call [004011D0h] ; __vbaStrMove
  loc_00416704: push eax
  loc_00416705: lea edx, var_40
  loc_00416708: push edx
  loc_00416709: call [00401044h] ; __vbaStrErrVarCopy
  loc_0041670F: mov edx, eax
  loc_00416711: lea ecx, var_50
  loc_00416714: call [004011D0h] ; __vbaStrMove
  loc_0041671A: push eax
  loc_0041671B: call [00401050h] ; __vbaStrCat
  loc_00416721: mov edx, eax
  loc_00416723: lea ecx, var_54
  loc_00416726: call [004011D0h] ; __vbaStrMove
  loc_0041672C: push eax
  loc_0041672D: push 004054D8h ; vbCrLf
  loc_00416732: call [00401050h] ; __vbaStrCat
  loc_00416738: mov edx, eax
  loc_0041673A: lea ecx, var_58
  loc_0041673D: call [004011D0h] ; __vbaStrMove
  loc_00416743: push eax
  loc_00416744: push 004054D8h ; vbCrLf
  loc_00416749: call [00401050h] ; __vbaStrCat
  loc_0041674F: mov edx, eax
  loc_00416751: lea ecx, var_5C
  loc_00416754: call [004011D0h] ; __vbaStrMove
  loc_0041675A: push eax
  loc_0041675B: push 004064ECh ; "Continue anyway?"
  loc_00416760: call [00401050h] ; __vbaStrCat
  loc_00416766: mov var_70, eax
  loc_00416769: mov var_78, 00000008h
  loc_00416770: lea eax, var_A8
  loc_00416776: push eax
  loc_00416777: lea ecx, var_98
  loc_0041677D: push ecx
  loc_0041677E: lea edx, var_88
  loc_00416784: push edx
  loc_00416785: push 00000024h
  loc_00416787: lea eax, var_78
  loc_0041678A: push eax
  loc_0041678B: call [00401084h] ; rtcMsgBox
  loc_00416791: mov ecx, eax
  loc_00416793: call [004010ECh] ; __vbaI2I4
  loc_00416799: mov var_24, ax
  loc_0041679D: lea ecx, var_5C
  loc_004167A0: push ecx
  loc_004167A1: lea edx, var_58
  loc_004167A4: push edx
  loc_004167A5: lea eax, var_54
  loc_004167A8: push eax
  loc_004167A9: lea ecx, var_50
  loc_004167AC: push ecx
  loc_004167AD: lea edx, var_4C
  loc_004167B0: push edx
  loc_004167B1: push 00000005h
  loc_004167B3: call [00401180h] ; __vbaFreeStrList
  loc_004167B9: add esp, 00000018h
  loc_004167BC: lea eax, var_A8
  loc_004167C2: push eax
  loc_004167C3: lea ecx, var_98
  loc_004167C9: push ecx
  loc_004167CA: lea edx, var_88
  loc_004167D0: push edx
  loc_004167D1: lea eax, var_78
  loc_004167D4: push eax
  loc_004167D5: push 00000004h
  loc_004167D7: call [00401038h] ; __vbaFreeVarList
  loc_004167DD: add esp, 00000014h
  loc_004167E0: mov var_4, 00000059h
  loc_004167E7: movsx ecx, var_24
  loc_004167EB: cmp ecx, 00000007h
  loc_004167EE: jnz 004167FDh
  loc_004167F0: mov var_4, 0000005Ah
  loc_004167F7: call [00401034h] ; __vbaEnd
  loc_004167FD: mov var_4, 0000005Dh
  loc_00416804: call [004010A0h] ; rtcDoEvents
  loc_0041680A: mov var_4, 0000005Eh
  loc_00416811: push 0040714Ch
  loc_00416816: call [00401110h] ; __vbaNew
  loc_0041681C: push eax
  loc_0041681D: lea edx, var_44
  loc_00416820: push edx
  loc_00416821: call [00401080h] ; __vbaObjSet
  loc_00416827: mov var_4, 0000005Fh
  loc_0041682E: push 00407160h ; "SELECT * FROM tblProberConfiguration "
  loc_00416833: push 004071B0h ; "WHERE tblProberConfiguration.fldProberName = 'LampElectrical' "
  loc_00416838: call [00401050h] ; __vbaStrCat
  loc_0041683E: mov edx, eax
  loc_00416840: lea ecx, var_4C
  loc_00416843: call [004011D0h] ; __vbaStrMove
  loc_00416849: push eax
  loc_0041684A: push 00407280h ; "ORDER BY tblProberConfiguration.fldInitializeOrder"
  loc_0041684F: call [00401050h] ; __vbaStrCat
  loc_00416855: mov edx, eax
  loc_00416857: lea ecx, var_28
  loc_0041685A: call [004011D0h] ; __vbaStrMove
  loc_00416860: lea ecx, var_4C
  loc_00416863: call [004011F4h] ; __vbaFreeStr
  loc_00416869: mov var_4, 00000060h
  loc_00416870: mov eax, [00423024h]
  loc_00416875: mov var_130, eax
  loc_0041687B: mov var_138, 00000009h
  loc_00416885: mov ecx, var_28
  loc_00416888: mov var_120, ecx
  loc_0041688E: mov var_128, 00000008h
  loc_00416898: push FFFFFFFFh
  loc_0041689A: push FFFFFFFFh
  loc_0041689C: push FFFFFFFFh
  loc_0041689E: mov eax, 00000010h
  loc_004168A3: call 00401AA0h ; __vbaChkstk
  loc_004168A8: mov edx, esp
  loc_004168AA: mov eax, var_138
  loc_004168B0: mov [edx], eax
  loc_004168B2: mov ecx, var_134
  loc_004168B8: mov [edx+00000004h], ecx
  loc_004168BB: mov eax, var_130
  loc_004168C1: mov [edx+00000008h], eax
  loc_004168C4: mov ecx, var_12C
  loc_004168CA: mov [edx+0000000Ch], ecx
  loc_004168CD: mov eax, 00000010h
  loc_004168D2: call 00401AA0h ; __vbaChkstk
  loc_004168D7: mov edx, esp
  loc_004168D9: mov eax, var_128
  loc_004168DF: mov [edx], eax
  loc_004168E1: mov ecx, var_124
  loc_004168E7: mov [edx+00000004h], ecx
  loc_004168EA: mov eax, var_120
  loc_004168F0: mov [edx+00000008h], eax
  loc_004168F3: mov ecx, var_11C
  loc_004168F9: mov [edx+0000000Ch], ecx
  loc_004168FC: mov edx, var_44
  loc_004168FF: mov eax, [edx]
  loc_00416901: mov ecx, var_44
  loc_00416904: push ecx
  loc_00416905: call [eax+000000A0h]
  loc_0041690B: fnclex
  loc_0041690D: mov var_1B8, eax
  loc_00416913: cmp var_1B8, 00000000h
  loc_0041691A: jge 0041693Fh
  loc_0041691C: push 000000A0h
  loc_00416921: push 004072E8h
  loc_00416926: mov edx, var_44
  loc_00416929: push edx
  loc_0041692A: mov eax, var_1B8
  loc_00416930: push eax
  loc_00416931: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00416937: mov var_2A0, eax
  loc_0041693D: jmp 00416949h
  loc_0041693F: mov var_2A0, 00000000h
  loc_00416949: mov var_4, 00000061h
  loc_00416950: lea ecx, var_1AC
  loc_00416956: push ecx
  loc_00416957: mov edx, var_44
  loc_0041695A: mov eax, [edx]
  loc_0041695C: mov ecx, var_44
  loc_0041695F: push ecx
  loc_00416960: call [eax+00000050h]
  loc_00416963: fnclex
  loc_00416965: mov var_1B8, eax
  loc_0041696B: cmp var_1B8, 00000000h
  loc_00416972: jge 00416994h
  loc_00416974: push 00000050h
  loc_00416976: push 004072E8h
  loc_0041697B: mov edx, var_44
  loc_0041697E: push edx
  loc_0041697F: mov eax, var_1B8
  loc_00416985: push eax
  loc_00416986: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041698C: mov var_2A4, eax
  loc_00416992: jmp 0041699Eh
  loc_00416994: mov var_2A4, 00000000h
  loc_0041699E: lea ecx, var_1B0
  loc_004169A4: push ecx
  loc_004169A5: mov edx, var_44
  loc_004169A8: mov eax, [edx]
  loc_004169AA: mov ecx, var_44
  loc_004169AD: push ecx
  loc_004169AE: call [eax+00000034h]
  loc_004169B1: fnclex
  loc_004169B3: mov var_1BC, eax
  loc_004169B9: cmp var_1BC, 00000000h
  loc_004169C0: jge 004169E2h
  loc_004169C2: push 00000034h
  loc_004169C4: push 004072E8h
  loc_004169C9: mov edx, var_44
  loc_004169CC: push edx
  loc_004169CD: mov eax, var_1BC
  loc_004169D3: push eax
  loc_004169D4: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004169DA: mov var_2A8, eax
  loc_004169E0: jmp 004169ECh
  loc_004169E2: mov var_2A8, 00000000h
  loc_004169EC: movsx ecx, var_1AC
  loc_004169F3: neg ecx
  loc_004169F5: sbb ecx, ecx
  loc_004169F7: inc ecx
  loc_004169F8: movsx edx, var_1B0
  loc_004169FF: neg edx
  loc_00416A01: sbb edx, edx
  loc_00416A03: inc edx
  loc_00416A04: or ecx, edx
  loc_00416A06: test ecx, ecx
  loc_00416A08: jnz 00416B85h
  loc_00416A0E: mov var_4, 00000062h
  loc_00416A15: mov eax, var_44
  loc_00416A18: mov ecx, [eax]
  loc_00416A1A: mov edx, var_44
  loc_00416A1D: push edx
  loc_00416A1E: call [ecx+00000080h]
  loc_00416A24: fnclex
  loc_00416A26: mov var_1B8, eax
  loc_00416A2C: cmp var_1B8, 00000000h
  loc_00416A33: jge 00416A58h
  loc_00416A35: push 00000080h
  loc_00416A3A: push 004072E8h
  loc_00416A3F: mov eax, var_44
  loc_00416A42: push eax
  loc_00416A43: mov ecx, var_1B8
  loc_00416A49: push ecx
  loc_00416A4A: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00416A50: mov var_2AC, eax
  loc_00416A56: jmp 00416A62h
  loc_00416A58: mov var_2AC, 00000000h
  loc_00416A62: mov var_4, 00000063h
  loc_00416A69: push 00407160h ; "SELECT * FROM tblProberConfiguration "
  loc_00416A6E: push 004072FCh ; "WHERE tblProberConfiguration.fldProberName = 'Default' "
  loc_00416A73: call [00401050h] ; __vbaStrCat
  loc_00416A79: mov edx, eax
  loc_00416A7B: lea ecx, var_4C
  loc_00416A7E: call [004011D0h] ; __vbaStrMove
  loc_00416A84: push eax
  loc_00416A85: push 00407280h ; "ORDER BY tblProberConfiguration.fldInitializeOrder"
  loc_00416A8A: call [00401050h] ; __vbaStrCat
  loc_00416A90: mov edx, eax
  loc_00416A92: lea ecx, var_28
  loc_00416A95: call [004011D0h] ; __vbaStrMove
  loc_00416A9B: lea ecx, var_4C
  loc_00416A9E: call [004011F4h] ; __vbaFreeStr
  loc_00416AA4: mov var_4, 00000064h
  loc_00416AAB: mov edx, [00423024h]
  loc_00416AB1: mov var_130, edx
  loc_00416AB7: mov var_138, 00000009h
  loc_00416AC1: mov eax, var_28
  loc_00416AC4: mov var_120, eax
  loc_00416ACA: mov var_128, 00000008h
  loc_00416AD4: push FFFFFFFFh
  loc_00416AD6: push FFFFFFFFh
  loc_00416AD8: push FFFFFFFFh
  loc_00416ADA: mov eax, 00000010h
  loc_00416ADF: call 00401AA0h ; __vbaChkstk
  loc_00416AE4: mov ecx, esp
  loc_00416AE6: mov edx, var_138
  loc_00416AEC: mov [ecx], edx
  loc_00416AEE: mov eax, var_134
  loc_00416AF4: mov [ecx+00000004h], eax
  loc_00416AF7: mov edx, var_130
  loc_00416AFD: mov [ecx+00000008h], edx
  loc_00416B00: mov eax, var_12C
  loc_00416B06: mov [ecx+0000000Ch], eax
  loc_00416B09: mov eax, 00000010h
  loc_00416B0E: call 00401AA0h ; __vbaChkstk
  loc_00416B13: mov ecx, esp
  loc_00416B15: mov edx, var_128
  loc_00416B1B: mov [ecx], edx
  loc_00416B1D: mov eax, var_124
  loc_00416B23: mov [ecx+00000004h], eax
  loc_00416B26: mov edx, var_120
  loc_00416B2C: mov [ecx+00000008h], edx
  loc_00416B2F: mov eax, var_11C
  loc_00416B35: mov [ecx+0000000Ch], eax
  loc_00416B38: mov ecx, var_44
  loc_00416B3B: mov edx, [ecx]
  loc_00416B3D: mov eax, var_44
  loc_00416B40: push eax
  loc_00416B41: call [edx+000000A0h]
  loc_00416B47: fnclex
  loc_00416B49: mov var_1B8, eax
  loc_00416B4F: cmp var_1B8, 00000000h
  loc_00416B56: jge 00416B7Bh
  loc_00416B58: push 000000A0h
  loc_00416B5D: push 004072E8h
  loc_00416B62: mov ecx, var_44
  loc_00416B65: push ecx
  loc_00416B66: mov edx, var_1B8
  loc_00416B6C: push edx
  loc_00416B6D: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00416B73: mov var_2B0, eax
  loc_00416B79: jmp 00416B85h
  loc_00416B7B: mov var_2B0, 00000000h
  loc_00416B85: mov var_4, 00000066h
  loc_00416B8C: lea eax, var_1AC
  loc_00416B92: push eax
  loc_00416B93: mov ecx, var_44
  loc_00416B96: mov edx, [ecx]
  loc_00416B98: mov eax, var_44
  loc_00416B9B: push eax
  loc_00416B9C: call [edx+00000050h]
  loc_00416B9F: fnclex
  loc_00416BA1: mov var_1B8, eax
  loc_00416BA7: cmp var_1B8, 00000000h
  loc_00416BAE: jge 00416BD0h
  loc_00416BB0: push 00000050h
  loc_00416BB2: push 004072E8h
  loc_00416BB7: mov ecx, var_44
  loc_00416BBA: push ecx
  loc_00416BBB: mov edx, var_1B8
  loc_00416BC1: push edx
  loc_00416BC2: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00416BC8: mov var_2B4, eax
  loc_00416BCE: jmp 00416BDAh
  loc_00416BD0: mov var_2B4, 00000000h
  loc_00416BDA: movsx eax, var_1AC
  loc_00416BE1: test eax, eax
  loc_00416BE3: jnz 004175F3h
  loc_00416BE9: mov var_4, 00000067h
  loc_00416BF0: lea ecx, var_64
  loc_00416BF3: push ecx
  loc_00416BF4: mov edx, var_44
  loc_00416BF7: mov eax, [edx]
  loc_00416BF9: mov ecx, var_44
  loc_00416BFC: push ecx
  loc_00416BFD: call [eax+00000054h]
  loc_00416C00: fnclex
  loc_00416C02: mov var_1B8, eax
  loc_00416C08: cmp var_1B8, 00000000h
  loc_00416C0F: jge 00416C31h
  loc_00416C11: push 00000054h
  loc_00416C13: push 004072E8h
  loc_00416C18: mov edx, var_44
  loc_00416C1B: push edx
  loc_00416C1C: mov eax, var_1B8
  loc_00416C22: push eax
  loc_00416C23: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00416C29: mov var_2B8, eax
  loc_00416C2F: jmp 00416C3Bh
  loc_00416C31: mov var_2B8, 00000000h
  loc_00416C3B: mov ecx, var_64
  loc_00416C3E: mov var_1BC, ecx
  loc_00416C44: mov var_120, 00407370h ; "fld2001XSyntax"
  loc_00416C4E: mov var_128, 00000008h
  loc_00416C58: lea edx, var_68
  loc_00416C5B: push edx
  loc_00416C5C: mov eax, 00000010h
  loc_00416C61: call 00401AA0h ; __vbaChkstk
  loc_00416C66: mov eax, esp
  loc_00416C68: mov ecx, var_128
  loc_00416C6E: mov [eax], ecx
  loc_00416C70: mov edx, var_124
  loc_00416C76: mov [eax+00000004h], edx
  loc_00416C79: mov ecx, var_120
  loc_00416C7F: mov [eax+00000008h], ecx
  loc_00416C82: mov edx, var_11C
  loc_00416C88: mov [eax+0000000Ch], edx
  loc_00416C8B: mov eax, var_1BC
  loc_00416C91: mov ecx, [eax]
  loc_00416C93: mov edx, var_1BC
  loc_00416C99: push edx
  loc_00416C9A: call [ecx+00000028h]
  loc_00416C9D: fnclex
  loc_00416C9F: mov var_1C0, eax
  loc_00416CA5: cmp var_1C0, 00000000h
  loc_00416CAC: jge 00416CD1h
  loc_00416CAE: push 00000028h
  loc_00416CB0: push 00407390h
  loc_00416CB5: mov eax, var_1BC
  loc_00416CBB: push eax
  loc_00416CBC: mov ecx, var_1C0
  loc_00416CC2: push ecx
  loc_00416CC3: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00416CC9: mov var_2BC, eax
  loc_00416CCF: jmp 00416CDBh
  loc_00416CD1: mov var_2BC, 00000000h
  loc_00416CDB: mov edx, var_68
  loc_00416CDE: mov var_1C4, edx
  loc_00416CE4: lea eax, var_78
  loc_00416CE7: push eax
  loc_00416CE8: mov ecx, var_1C4
  loc_00416CEE: mov edx, [ecx]
  loc_00416CF0: mov eax, var_1C4
  loc_00416CF6: push eax
  loc_00416CF7: call [edx+00000034h]
  loc_00416CFA: fnclex
  loc_00416CFC: mov var_1C8, eax
  loc_00416D02: cmp var_1C8, 00000000h
  loc_00416D09: jge 00416D2Eh
  loc_00416D0B: push 00000034h
  loc_00416D0D: push 004073A0h
  loc_00416D12: mov ecx, var_1C4
  loc_00416D18: push ecx
  loc_00416D19: mov edx, var_1C8
  loc_00416D1F: push edx
  loc_00416D20: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00416D26: mov var_2C0, eax
  loc_00416D2C: jmp 00416D38h
  loc_00416D2E: mov var_2C0, 00000000h
  loc_00416D38: mov var_130, 00000000h
  loc_00416D42: mov var_138, 00008008h
  loc_00416D4C: lea eax, var_78
  loc_00416D4F: push eax
  loc_00416D50: lea ecx, var_138
  loc_00416D56: push ecx
  loc_00416D57: call [00401198h] ; __vbaVarTstNe
  loc_00416D5D: mov var_1CC, ax
  loc_00416D64: lea edx, var_68
  loc_00416D67: push edx
  loc_00416D68: lea eax, var_64
  loc_00416D6B: push eax
  loc_00416D6C: push 00000002h
  loc_00416D6E: call [00401040h] ; __vbaFreeObjList
  loc_00416D74: add esp, 0000000Ch
  loc_00416D77: lea ecx, var_78
  loc_00416D7A: call [00401020h] ; __vbaFreeVar
  loc_00416D80: movsx ecx, var_1CC
  loc_00416D87: test ecx, ecx
  loc_00416D89: jz 0041758Dh
  loc_00416D8F: mov var_4, 00000068h
  loc_00416D96: xor edx, edx
  loc_00416D98: test edx, edx
  loc_00416D9A: jz 00416FB3h
  loc_00416DA0: mov var_4, 00000069h
  loc_00416DA7: mov var_B0, 80020004h
  loc_00416DB1: mov var_B8, 0000000Ah
  loc_00416DBB: mov var_A0, 80020004h
  loc_00416DC5: mov var_A8, 0000000Ah
  loc_00416DCF: mov var_90, 80020004h
  loc_00416DD9: mov var_98, 0000000Ah
  loc_00416DE3: mov var_130, 004073B4h ; "tblProberConfiguration open: "
  loc_00416DED: mov var_138, 00000008h
  loc_00416DF7: lea eax, var_64
  loc_00416DFA: push eax
  loc_00416DFB: mov ecx, var_44
  loc_00416DFE: mov edx, [ecx]
  loc_00416E00: mov eax, var_44
  loc_00416E03: push eax
  loc_00416E04: call [edx+00000054h]
  loc_00416E07: fnclex
  loc_00416E09: mov var_1B8, eax
  loc_00416E0F: cmp var_1B8, 00000000h
  loc_00416E16: jge 00416E38h
  loc_00416E18: push 00000054h
  loc_00416E1A: push 004072E8h
  loc_00416E1F: mov ecx, var_44
  loc_00416E22: push ecx
  loc_00416E23: mov edx, var_1B8
  loc_00416E29: push edx
  loc_00416E2A: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00416E30: mov var_2C4, eax
  loc_00416E36: jmp 00416E42h
  loc_00416E38: mov var_2C4, 00000000h
  loc_00416E42: mov eax, var_64
  loc_00416E45: mov var_1BC, eax
  loc_00416E4B: mov var_120, 00407370h ; "fld2001XSyntax"
  loc_00416E55: mov var_128, 00000008h
  loc_00416E5F: lea ecx, var_68
  loc_00416E62: push ecx
  loc_00416E63: mov eax, 00000010h
  loc_00416E68: call 00401AA0h ; __vbaChkstk
  loc_00416E6D: mov edx, esp
  loc_00416E6F: mov eax, var_128
  loc_00416E75: mov [edx], eax
  loc_00416E77: mov ecx, var_124
  loc_00416E7D: mov [edx+00000004h], ecx
  loc_00416E80: mov eax, var_120
  loc_00416E86: mov [edx+00000008h], eax
  loc_00416E89: mov ecx, var_11C
  loc_00416E8F: mov [edx+0000000Ch], ecx
  loc_00416E92: mov edx, var_1BC
  loc_00416E98: mov eax, [edx]
  loc_00416E9A: mov ecx, var_1BC
  loc_00416EA0: push ecx
  loc_00416EA1: call [eax+00000028h]
  loc_00416EA4: fnclex
  loc_00416EA6: mov var_1C0, eax
  loc_00416EAC: cmp var_1C0, 00000000h
  loc_00416EB3: jge 00416ED8h
  loc_00416EB5: push 00000028h
  loc_00416EB7: push 00407390h
  loc_00416EBC: mov edx, var_1BC
  loc_00416EC2: push edx
  loc_00416EC3: mov eax, var_1C0
  loc_00416EC9: push eax
  loc_00416ECA: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00416ED0: mov var_2C8, eax
  loc_00416ED6: jmp 00416EE2h
  loc_00416ED8: mov var_2C8, 00000000h
  loc_00416EE2: mov ecx, var_68
  loc_00416EE5: mov var_1C4, ecx
  loc_00416EEB: lea edx, var_78
  loc_00416EEE: push edx
  loc_00416EEF: mov eax, var_1C4
  loc_00416EF5: mov ecx, [eax]
  loc_00416EF7: mov edx, var_1C4
  loc_00416EFD: push edx
  loc_00416EFE: call [ecx+00000034h]
  loc_00416F01: fnclex
  loc_00416F03: mov var_1C8, eax
  loc_00416F09: cmp var_1C8, 00000000h
  loc_00416F10: jge 00416F35h
  loc_00416F12: push 00000034h
  loc_00416F14: push 004073A0h
  loc_00416F19: mov eax, var_1C4
  loc_00416F1F: push eax
  loc_00416F20: mov ecx, var_1C8
  loc_00416F26: push ecx
  loc_00416F27: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00416F2D: mov var_2CC, eax
  loc_00416F33: jmp 00416F3Fh
  loc_00416F35: mov var_2CC, 00000000h
  loc_00416F3F: lea edx, var_B8
  loc_00416F45: push edx
  loc_00416F46: lea eax, var_A8
  loc_00416F4C: push eax
  loc_00416F4D: lea ecx, var_98
  loc_00416F53: push ecx
  loc_00416F54: push 00000000h
  loc_00416F56: lea edx, var_138
  loc_00416F5C: push edx
  loc_00416F5D: lea eax, var_78
  loc_00416F60: push eax
  loc_00416F61: lea ecx, var_88
  loc_00416F67: push ecx
  loc_00416F68: call [004011ACh] ; __vbaVarAdd
  loc_00416F6E: push eax
  loc_00416F6F: call [00401084h] ; rtcMsgBox
  loc_00416F75: lea edx, var_68
  loc_00416F78: push edx
  loc_00416F79: lea eax, var_64
  loc_00416F7C: push eax
  loc_00416F7D: push 00000002h
  loc_00416F7F: call [00401040h] ; __vbaFreeObjList
  loc_00416F85: add esp, 0000000Ch
  loc_00416F88: lea ecx, var_B8
  loc_00416F8E: push ecx
  loc_00416F8F: lea edx, var_A8
  loc_00416F95: push edx
  loc_00416F96: lea eax, var_98
  loc_00416F9C: push eax
  loc_00416F9D: lea ecx, var_88
  loc_00416FA3: push ecx
  loc_00416FA4: lea edx, var_78
  loc_00416FA7: push edx
  loc_00416FA8: push 00000005h
  loc_00416FAA: call [00401038h] ; __vbaFreeVarList
  loc_00416FB0: add esp, 00000018h
  loc_00416FB3: mov var_4, 0000006Bh
  loc_00416FBA: lea eax, var_64
  loc_00416FBD: push eax
  loc_00416FBE: mov ecx, var_44
  loc_00416FC1: mov edx, [ecx]
  loc_00416FC3: mov eax, var_44
  loc_00416FC6: push eax
  loc_00416FC7: call [edx+00000054h]
  loc_00416FCA: fnclex
  loc_00416FCC: mov var_1B8, eax
  loc_00416FD2: cmp var_1B8, 00000000h
  loc_00416FD9: jge 00416FFBh
  loc_00416FDB: push 00000054h
  loc_00416FDD: push 004072E8h
  loc_00416FE2: mov ecx, var_44
  loc_00416FE5: push ecx
  loc_00416FE6: mov edx, var_1B8
  loc_00416FEC: push edx
  loc_00416FED: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00416FF3: mov var_2D0, eax
  loc_00416FF9: jmp 00417005h
  loc_00416FFB: mov var_2D0, 00000000h
  loc_00417005: mov eax, var_64
  loc_00417008: mov var_1BC, eax
  loc_0041700E: mov var_120, 00407370h ; "fld2001XSyntax"
  loc_00417018: mov var_128, 00000008h
  loc_00417022: lea ecx, var_68
  loc_00417025: push ecx
  loc_00417026: mov eax, 00000010h
  loc_0041702B: call 00401AA0h ; __vbaChkstk
  loc_00417030: mov edx, esp
  loc_00417032: mov eax, var_128
  loc_00417038: mov [edx], eax
  loc_0041703A: mov ecx, var_124
  loc_00417040: mov [edx+00000004h], ecx
  loc_00417043: mov eax, var_120
  loc_00417049: mov [edx+00000008h], eax
  loc_0041704C: mov ecx, var_11C
  loc_00417052: mov [edx+0000000Ch], ecx
  loc_00417055: mov edx, var_1BC
  loc_0041705B: mov eax, [edx]
  loc_0041705D: mov ecx, var_1BC
  loc_00417063: push ecx
  loc_00417064: call [eax+00000028h]
  loc_00417067: fnclex
  loc_00417069: mov var_1C0, eax
  loc_0041706F: cmp var_1C0, 00000000h
  loc_00417076: jge 0041709Bh
  loc_00417078: push 00000028h
  loc_0041707A: push 00407390h
  loc_0041707F: mov edx, var_1BC
  loc_00417085: push edx
  loc_00417086: mov eax, var_1C0
  loc_0041708C: push eax
  loc_0041708D: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00417093: mov var_2D4, eax
  loc_00417099: jmp 004170A5h
  loc_0041709B: mov var_2D4, 00000000h
  loc_004170A5: mov ecx, var_68
  loc_004170A8: mov var_1C4, ecx
  loc_004170AE: lea edx, var_78
  loc_004170B1: push edx
  loc_004170B2: mov eax, var_1C4
  loc_004170B8: mov ecx, [eax]
  loc_004170BA: mov edx, var_1C4
  loc_004170C0: push edx
  loc_004170C1: call [ecx+00000034h]
  loc_004170C4: fnclex
  loc_004170C6: mov var_1C8, eax
  loc_004170CC: cmp var_1C8, 00000000h
  loc_004170D3: jge 004170F8h
  loc_004170D5: push 00000034h
  loc_004170D7: push 004073A0h
  loc_004170DC: mov eax, var_1C4
  loc_004170E2: push eax
  loc_004170E3: mov ecx, var_1C8
  loc_004170E9: push ecx
  loc_004170EA: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004170F0: mov var_2D8, eax
  loc_004170F6: jmp 00417102h
  loc_004170F8: mov var_2D8, 00000000h
  loc_00417102: mov var_80, FFFFFFFFh
  loc_00417109: mov var_88, 0000000Bh
  loc_00417113: lea edx, var_78
  loc_00417116: push edx
  loc_00417117: call [00401030h] ; __vbaStrVarMove
  loc_0041711D: mov edx, eax
  loc_0041711F: lea ecx, var_50
  loc_00417122: call [004011D0h] ; __vbaStrMove
  loc_00417128: mov edx, 00406454h ; "2001X"
  loc_0041712D: lea ecx, var_4C
  loc_00417130: call [00401178h] ; __vbaStrCopy
  loc_00417136: lea eax, var_88
  loc_0041713C: push eax
  loc_0041713D: lea ecx, var_50
  loc_00417140: push ecx
  loc_00417141: lea edx, var_4C
  loc_00417144: push edx
  loc_00417145: lea eax, var_98
  loc_0041714B: push eax
  loc_0041714C: call 0041CA40h
  loc_00417151: lea edx, var_98
  loc_00417157: lea ecx, var_40
  loc_0041715A: call [00401014h] ; __vbaVarMove
  loc_00417160: lea ecx, var_50
  loc_00417163: push ecx
  loc_00417164: lea edx, var_4C
  loc_00417167: push edx
  loc_00417168: push 00000002h
  loc_0041716A: call [00401180h] ; __vbaFreeStrList
  loc_00417170: add esp, 0000000Ch
  loc_00417173: lea eax, var_68
  loc_00417176: push eax
  loc_00417177: lea ecx, var_64
  loc_0041717A: push ecx
  loc_0041717B: push 00000002h
  loc_0041717D: call [00401040h] ; __vbaFreeObjList
  loc_00417183: add esp, 0000000Ch
  loc_00417186: lea edx, var_88
  loc_0041718C: push edx
  loc_0041718D: lea eax, var_78
  loc_00417190: push eax
  loc_00417191: push 00000002h
  loc_00417193: call [00401038h] ; __vbaFreeVarList
  loc_00417199: add esp, 0000000Ch
  loc_0041719C: mov var_4, 0000006Ch
  loc_004171A3: lea ecx, var_40
  loc_004171A6: push ecx
  loc_004171A7: call [00401044h] ; __vbaStrErrVarCopy
  loc_004171AD: mov edx, eax
  loc_004171AF: lea ecx, var_4C
  loc_004171B2: call [004011D0h] ; __vbaStrMove
  loc_004171B8: push eax
  loc_004171B9: push 00406464h ; "MC"
  loc_004171BE: call [004010DCh] ; __vbaStrCmp
  loc_004171C4: neg eax
  loc_004171C6: sbb eax, eax
  loc_004171C8: neg eax
  loc_004171CA: neg eax
  loc_004171CC: mov var_1B8, ax
  loc_004171D3: lea ecx, var_4C
  loc_004171D6: call [004011F4h] ; __vbaFreeStr
  loc_004171DC: movsx edx, var_1B8
  loc_004171E3: test edx, edx
  loc_004171E5: jz 0041758Dh
  loc_004171EB: mov var_4, 0000006Dh
  loc_004171F2: lea eax, var_64
  loc_004171F5: push eax
  loc_004171F6: mov ecx, var_44
  loc_004171F9: mov edx, [ecx]
  loc_004171FB: mov eax, var_44
  loc_004171FE: push eax
  loc_004171FF: call [edx+00000054h]
  loc_00417202: fnclex
  loc_00417204: mov var_1B8, eax
  loc_0041720A: cmp var_1B8, 00000000h
  loc_00417211: jge 00417233h
  loc_00417213: push 00000054h
  loc_00417215: push 004072E8h
  loc_0041721A: mov ecx, var_44
  loc_0041721D: push ecx
  loc_0041721E: mov edx, var_1B8
  loc_00417224: push edx
  loc_00417225: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041722B: mov var_2DC, eax
  loc_00417231: jmp 0041723Dh
  loc_00417233: mov var_2DC, 00000000h
  loc_0041723D: mov eax, var_64
  loc_00417240: mov var_1BC, eax
  loc_00417246: mov var_120, 00407370h ; "fld2001XSyntax"
  loc_00417250: mov var_128, 00000008h
  loc_0041725A: lea ecx, var_68
  loc_0041725D: push ecx
  loc_0041725E: mov eax, 00000010h
  loc_00417263: call 00401AA0h ; __vbaChkstk
  loc_00417268: mov edx, esp
  loc_0041726A: mov eax, var_128
  loc_00417270: mov [edx], eax
  loc_00417272: mov ecx, var_124
  loc_00417278: mov [edx+00000004h], ecx
  loc_0041727B: mov eax, var_120
  loc_00417281: mov [edx+00000008h], eax
  loc_00417284: mov ecx, var_11C
  loc_0041728A: mov [edx+0000000Ch], ecx
  loc_0041728D: mov edx, var_1BC
  loc_00417293: mov eax, [edx]
  loc_00417295: mov ecx, var_1BC
  loc_0041729B: push ecx
  loc_0041729C: call [eax+00000028h]
  loc_0041729F: fnclex
  loc_004172A1: mov var_1C0, eax
  loc_004172A7: cmp var_1C0, 00000000h
  loc_004172AE: jge 004172D3h
  loc_004172B0: push 00000028h
  loc_004172B2: push 00407390h
  loc_004172B7: mov edx, var_1BC
  loc_004172BD: push edx
  loc_004172BE: mov eax, var_1C0
  loc_004172C4: push eax
  loc_004172C5: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004172CB: mov var_2E0, eax
  loc_004172D1: jmp 004172DDh
  loc_004172D3: mov var_2E0, 00000000h
  loc_004172DD: mov ecx, var_68
  loc_004172E0: mov var_1C4, ecx
  loc_004172E6: lea edx, var_78
  loc_004172E9: push edx
  loc_004172EA: mov eax, var_1C4
  loc_004172F0: mov ecx, [eax]
  loc_004172F2: mov edx, var_1C4
  loc_004172F8: push edx
  loc_004172F9: call [ecx+00000034h]
  loc_004172FC: fnclex
  loc_004172FE: mov var_1C8, eax
  loc_00417304: cmp var_1C8, 00000000h
  loc_0041730B: jge 00417330h
  loc_0041730D: push 00000034h
  loc_0041730F: push 004073A0h
  loc_00417314: mov eax, var_1C4
  loc_0041731A: push eax
  loc_0041731B: mov ecx, var_1C8
  loc_00417321: push ecx
  loc_00417322: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00417328: mov var_2E4, eax
  loc_0041732E: jmp 0041733Ah
  loc_00417330: mov var_2E4, 00000000h
  loc_0041733A: mov var_110, 80020004h
  loc_00417344: mov var_118, 0000000Ah
  loc_0041734E: mov var_100, 80020004h
  loc_00417358: mov var_108, 0000000Ah
  loc_00417362: mov var_180, 004050E8h ; "IMT LampElectrical Probing"
  loc_0041736C: mov var_188, 00000008h
  loc_00417376: lea edx, var_188
  loc_0041737C: lea ecx, var_F8
  loc_00417382: call [004011B4h] ; __vbaVarDup
  loc_00417388: mov var_130, 00406470h ; "Prober command '"
  loc_00417392: mov var_138, 00000008h
  loc_0041739C: mov var_140, 00406498h ; "' failed to return 'MC', instead said:"
  loc_004173A6: mov var_148, 00000008h
  loc_004173B0: mov var_150, 004054D8h ; vbCrLf
  loc_004173BA: mov var_158, 00000008h
  loc_004173C4: lea edx, var_40
  loc_004173C7: push edx
  loc_004173C8: call [00401044h] ; __vbaStrErrVarCopy
  loc_004173CE: mov var_B0, eax
  loc_004173D4: mov var_B8, 00000008h
  loc_004173DE: mov var_160, 004054D8h ; vbCrLf
  loc_004173E8: mov var_168, 00000008h
  loc_004173F2: mov var_170, 004064ECh ; "Continue anyway?"
  loc_004173FC: mov var_178, 00000008h
  loc_00417406: lea eax, var_118
  loc_0041740C: push eax
  loc_0041740D: lea ecx, var_108
  loc_00417413: push ecx
  loc_00417414: lea edx, var_F8
  loc_0041741A: push edx
  loc_0041741B: push 00000004h
  loc_0041741D: lea eax, var_138
  loc_00417423: push eax
  loc_00417424: lea ecx, var_78
  loc_00417427: push ecx
  loc_00417428: lea edx, var_88
  loc_0041742E: push edx
  loc_0041742F: call [004011ACh] ; __vbaVarAdd
  loc_00417435: push eax
  loc_00417436: lea eax, var_148
  loc_0041743C: push eax
  loc_0041743D: lea ecx, var_98
  loc_00417443: push ecx
  loc_00417444: call [004011ACh] ; __vbaVarAdd
  loc_0041744A: push eax
  loc_0041744B: lea edx, var_158
  loc_00417451: push edx
  loc_00417452: lea eax, var_A8
  loc_00417458: push eax
  loc_00417459: call [004011ACh] ; __vbaVarAdd
  loc_0041745F: push eax
  loc_00417460: lea ecx, var_B8
  loc_00417466: push ecx
  loc_00417467: lea edx, var_C8
  loc_0041746D: push edx
  loc_0041746E: call [004011ACh] ; __vbaVarAdd
  loc_00417474: push eax
  loc_00417475: lea eax, var_168
  loc_0041747B: push eax
  loc_0041747C: lea ecx, var_D8
  loc_00417482: push ecx
  loc_00417483: call [004011ACh] ; __vbaVarAdd
  loc_00417489: push eax
  loc_0041748A: lea edx, var_178
  loc_00417490: push edx
  loc_00417491: lea eax, var_E8
  loc_00417497: push eax
  loc_00417498: call [004011ACh] ; __vbaVarAdd
  loc_0041749E: push eax
  loc_0041749F: call [00401084h] ; rtcMsgBox
  loc_004174A5: mov ecx, eax
  loc_004174A7: call [004010ECh] ; __vbaI2I4
  loc_004174AD: mov var_24, ax
  loc_004174B1: lea ecx, var_68
  loc_004174B4: push ecx
  loc_004174B5: lea edx, var_64
  loc_004174B8: push edx
  loc_004174B9: push 00000002h
  loc_004174BB: call [00401040h] ; __vbaFreeObjList
  loc_004174C1: add esp, 0000000Ch
  loc_004174C4: lea eax, var_118
  loc_004174CA: push eax
  loc_004174CB: lea ecx, var_108
  loc_004174D1: push ecx
  loc_004174D2: lea edx, var_F8
  loc_004174D8: push edx
  loc_004174D9: lea eax, var_E8
  loc_004174DF: push eax
  loc_004174E0: lea ecx, var_D8
  loc_004174E6: push ecx
  loc_004174E7: lea edx, var_C8
  loc_004174ED: push edx
  loc_004174EE: lea eax, var_B8
  loc_004174F4: push eax
  loc_004174F5: lea ecx, var_A8
  loc_004174FB: push ecx
  loc_004174FC: lea edx, var_98
  loc_00417502: push edx
  loc_00417503: lea eax, var_88
  loc_00417509: push eax
  loc_0041750A: lea ecx, var_78
  loc_0041750D: push ecx
  loc_0041750E: push 0000000Bh
  loc_00417510: call [00401038h] ; __vbaFreeVarList
  loc_00417516: add esp, 00000030h
  loc_00417519: mov var_4, 0000006Eh
  loc_00417520: movsx edx, var_24
  loc_00417524: cmp edx, 00000007h
  loc_00417527: jnz 0041758Dh
  loc_00417529: mov var_4, 0000006Fh
  loc_00417530: lea eax, var_78
  loc_00417533: push eax
  loc_00417534: mov ecx, Me
  loc_00417537: mov edx, [ecx]
  loc_00417539: mov eax, Me
  loc_0041753C: push eax
  loc_0041753D: call [edx+00000704h]
  loc_00417543: mov var_1B8, eax
  loc_00417549: cmp var_1B8, 00000000h
  loc_00417550: jge 00417575h
  loc_00417552: push 00000704h
  loc_00417557: push 0040579Ch ; "#]=VｫoyAｷ ;ﾑs：ﾚLabel12"
  loc_0041755C: mov ecx, Me
  loc_0041755F: push ecx
  loc_00417560: mov edx, var_1B8
  loc_00417566: push edx
  loc_00417567: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041756D: mov var_2E8, eax
  loc_00417573: jmp 0041757Fh
  loc_00417575: mov var_2E8, 00000000h
  loc_0041757F: lea ecx, var_78
  loc_00417582: call [00401020h] ; __vbaFreeVar
  loc_00417588: jmp 00418D07h
  loc_0041758D: mov var_4, 00000074h
  loc_00417594: mov eax, var_44
  loc_00417597: mov ecx, [eax]
  loc_00417599: mov edx, var_44
  loc_0041759C: push edx
  loc_0041759D: call [ecx+00000090h]
  loc_004175A3: fnclex
  loc_004175A5: mov var_1B8, eax
  loc_004175AB: cmp var_1B8, 00000000h
  loc_004175B2: jge 004175D7h
  loc_004175B4: push 00000090h
  loc_004175B9: push 004072E8h
  loc_004175BE: mov eax, var_44
  loc_004175C1: push eax
  loc_004175C2: mov ecx, var_1B8
  loc_004175C8: push ecx
  loc_004175C9: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004175CF: mov var_2EC, eax
  loc_004175D5: jmp 004175E1h
  loc_004175D7: mov var_2EC, 00000000h
  loc_004175E1: mov var_4, 00000075h
  loc_004175E8: call [004010A0h] ; rtcDoEvents
  loc_004175EE: jmp 00416B85h
  loc_004175F3: mov var_4, 00000077h
  loc_004175FA: mov edx, var_44
  loc_004175FD: mov eax, [edx]
  loc_004175FF: mov ecx, var_44
  loc_00417602: push ecx
  loc_00417603: call [eax+00000080h]
  loc_00417609: fnclex
  loc_0041760B: mov var_1B8, eax
  loc_00417611: cmp var_1B8, 00000000h
  loc_00417618: jge 0041763Dh
  loc_0041761A: push 00000080h
  loc_0041761F: push 004072E8h
  loc_00417624: mov edx, var_44
  loc_00417627: push edx
  loc_00417628: mov eax, var_1B8
  loc_0041762E: push eax
  loc_0041762F: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00417635: mov var_2F0, eax
  loc_0041763B: jmp 00417647h
  loc_0041763D: mov var_2F0, 00000000h
  loc_00417647: mov var_4, 00000078h
  loc_0041764E: push 0040713Ch
  loc_00417653: push 00000000h
  loc_00417655: call [004011D4h] ; __vbaCastObj
  loc_0041765B: push eax
  loc_0041765C: lea ecx, var_44
  loc_0041765F: push ecx
  loc_00417660: call [00401080h] ; __vbaObjSet
  loc_00417666: mov var_4, 00000079h
  loc_0041766D: mov edx, 00407404h ; "DieSizeX"
  loc_00417672: lea ecx, var_4C
  loc_00417675: call [00401178h] ; __vbaStrCopy
  loc_0041767B: lea edx, var_50
  loc_0041767E: push edx
  loc_0041767F: lea eax, var_4C
  loc_00417682: push eax
  loc_00417683: mov ecx, var_48
  loc_00417686: mov edx, [ecx]
  loc_00417688: mov eax, var_48
  loc_0041768B: push eax
  loc_0041768C: call [edx+0000002Ch]
  loc_0041768F: fnclex
  loc_00417691: mov var_1B8, eax
  loc_00417697: cmp var_1B8, 00000000h
  loc_0041769E: jge 004176C0h
  loc_004176A0: push 0000002Ch
  loc_004176A2: push 00405B8Ch
  loc_004176A7: mov ecx, var_48
  loc_004176AA: push ecx
  loc_004176AB: mov edx, var_1B8
  loc_004176B1: push edx
  loc_004176B2: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004176B8: mov var_2F4, eax
  loc_004176BE: jmp 004176CAh
  loc_004176C0: mov var_2F4, 00000000h
  loc_004176CA: mov edx, 0040741Ch ; "DieSizeY"
  loc_004176CF: lea ecx, var_58
  loc_004176D2: call [00401178h] ; __vbaStrCopy
  loc_004176D8: lea eax, var_5C
  loc_004176DB: push eax
  loc_004176DC: lea ecx, var_58
  loc_004176DF: push ecx
  loc_004176E0: mov edx, var_48
  loc_004176E3: mov eax, [edx]
  loc_004176E5: mov ecx, var_48
  loc_004176E8: push ecx
  loc_004176E9: call [eax+0000002Ch]
  loc_004176EC: fnclex
  loc_004176EE: mov var_1BC, eax
  loc_004176F4: cmp var_1BC, 00000000h
  loc_004176FB: jge 0041771Dh
  loc_004176FD: push 0000002Ch
  loc_004176FF: push 00405B8Ch
  loc_00417704: mov edx, var_48
  loc_00417707: push edx
  loc_00417708: mov eax, var_1BC
  loc_0041770E: push eax
  loc_0041770F: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00417715: mov var_2F8, eax
  loc_0041771B: jmp 00417727h
  loc_0041771D: mov var_2F8, 00000000h
  loc_00417727: push 004073F4h ; "SP1X"
  loc_0041772C: mov ecx, var_50
  loc_0041772F: push ecx
  loc_00417730: call [00401050h] ; __vbaStrCat
  loc_00417736: mov edx, eax
  loc_00417738: lea ecx, var_54
  loc_0041773B: call [004011D0h] ; __vbaStrMove
  loc_00417741: push eax
  loc_00417742: push 0040644Ch ; "Y"
  loc_00417747: call [00401050h] ; __vbaStrCat
  loc_0041774D: mov edx, eax
  loc_0041774F: lea ecx, var_60
  loc_00417752: call [004011D0h] ; __vbaStrMove
  loc_00417758: push eax
  loc_00417759: mov edx, var_5C
  loc_0041775C: push edx
  loc_0041775D: call [00401050h] ; __vbaStrCat
  loc_00417763: mov edx, eax
  loc_00417765: lea ecx, var_2C
  loc_00417768: call [004011D0h] ; __vbaStrMove
  loc_0041776E: lea eax, var_5C
  loc_00417771: push eax
  loc_00417772: lea ecx, var_60
  loc_00417775: push ecx
  loc_00417776: lea edx, var_58
  loc_00417779: push edx
  loc_0041777A: lea eax, var_54
  loc_0041777D: push eax
  loc_0041777E: lea ecx, var_50
  loc_00417781: push ecx
  loc_00417782: lea edx, var_4C
  loc_00417785: push edx
  loc_00417786: push 00000006h
  loc_00417788: call [00401180h] ; __vbaFreeStrList
  loc_0041778E: add esp, 0000001Ch
  loc_00417791: mov var_4, 0000007Ah
  loc_00417798: mov var_70, FFFFFFFFh
  loc_0041779F: mov var_78, 0000000Bh
  loc_004177A6: mov edx, 00406454h ; "2001X"
  loc_004177AB: lea ecx, var_4C
  loc_004177AE: call [00401178h] ; __vbaStrCopy
  loc_004177B4: lea eax, var_78
  loc_004177B7: push eax
  loc_004177B8: lea ecx, var_2C
  loc_004177BB: push ecx
  loc_004177BC: lea edx, var_4C
  loc_004177BF: push edx
  loc_004177C0: lea eax, var_88
  loc_004177C6: push eax
  loc_004177C7: call 0041CA40h
  loc_004177CC: lea edx, var_88
  loc_004177D2: lea ecx, var_40
  loc_004177D5: call [00401014h] ; __vbaVarMove
  loc_004177DB: lea ecx, var_4C
  loc_004177DE: call [004011F4h] ; __vbaFreeStr
  loc_004177E4: lea ecx, var_78
  loc_004177E7: call [00401020h] ; __vbaFreeVar
  loc_004177ED: mov var_4, 0000007Bh
  loc_004177F4: lea ecx, var_40
  loc_004177F7: push ecx
  loc_004177F8: call [00401044h] ; __vbaStrErrVarCopy
  loc_004177FE: mov edx, eax
  loc_00417800: lea ecx, var_4C
  loc_00417803: call [004011D0h] ; __vbaStrMove
  loc_00417809: push eax
  loc_0041780A: push 00406464h ; "MC"
  loc_0041780F: call [004010DCh] ; __vbaStrCmp
  loc_00417815: neg eax
  loc_00417817: sbb eax, eax
  loc_00417819: neg eax
  loc_0041781B: neg eax
  loc_0041781D: mov var_1B8, ax
  loc_00417824: lea ecx, var_4C
  loc_00417827: call [004011F4h] ; __vbaFreeStr
  loc_0041782D: movsx edx, var_1B8
  loc_00417834: test edx, edx
  loc_00417836: jz 00417A16h
  loc_0041783C: mov var_4, 0000007Ch
  loc_00417843: mov var_A0, 80020004h
  loc_0041784D: mov var_A8, 0000000Ah
  loc_00417857: mov var_90, 80020004h
  loc_00417861: mov var_98, 0000000Ah
  loc_0041786B: mov var_120, 004050E8h ; "IMT LampElectrical Probing"
  loc_00417875: mov var_128, 00000008h
  loc_0041787F: lea edx, var_128
  loc_00417885: lea ecx, var_88
  loc_0041788B: call [004011B4h] ; __vbaVarDup
  loc_00417891: push 00406470h ; "Prober command '"
  loc_00417896: mov eax, var_2C
  loc_00417899: push eax
  loc_0041789A: call [00401050h] ; __vbaStrCat
  loc_004178A0: mov edx, eax
  loc_004178A2: lea ecx, var_4C
  loc_004178A5: call [004011D0h] ; __vbaStrMove
  loc_004178AB: push eax
  loc_004178AC: push 00406498h ; "' failed to return 'MC', instead said:"
  loc_004178B1: call [00401050h] ; __vbaStrCat
  loc_004178B7: mov edx, eax
  loc_004178B9: lea ecx, var_50
  loc_004178BC: call [004011D0h] ; __vbaStrMove
  loc_004178C2: push eax
  loc_004178C3: push 004054D8h ; vbCrLf
  loc_004178C8: call [00401050h] ; __vbaStrCat
  loc_004178CE: mov edx, eax
  loc_004178D0: lea ecx, var_54
  loc_004178D3: call [004011D0h] ; __vbaStrMove
  loc_004178D9: push eax
  loc_004178DA: lea ecx, var_40
  loc_004178DD: push ecx
  loc_004178DE: call [00401044h] ; __vbaStrErrVarCopy
  loc_004178E4: mov edx, eax
  loc_004178E6: lea ecx, var_58
  loc_004178E9: call [004011D0h] ; __vbaStrMove
  loc_004178EF: push eax
  loc_004178F0: call [00401050h] ; __vbaStrCat
  loc_004178F6: mov edx, eax
  loc_004178F8: lea ecx, var_5C
  loc_004178FB: call [004011D0h] ; __vbaStrMove
  loc_00417901: push eax
  loc_00417902: push 004054D8h ; vbCrLf
  loc_00417907: call [00401050h] ; __vbaStrCat
  loc_0041790D: mov edx, eax
  loc_0041790F: lea ecx, var_60
  loc_00417912: call [004011D0h] ; __vbaStrMove
  loc_00417918: push eax
  loc_00417919: push 004064ECh ; "Continue anyway?"
  loc_0041791E: call [00401050h] ; __vbaStrCat
  loc_00417924: mov var_70, eax
  loc_00417927: mov var_78, 00000008h
  loc_0041792E: lea edx, var_A8
  loc_00417934: push edx
  loc_00417935: lea eax, var_98
  loc_0041793B: push eax
  loc_0041793C: lea ecx, var_88
  loc_00417942: push ecx
  loc_00417943: push 00000004h
  loc_00417945: lea edx, var_78
  loc_00417948: push edx
  loc_00417949: call [00401084h] ; rtcMsgBox
  loc_0041794F: mov ecx, eax
  loc_00417951: call [004010ECh] ; __vbaI2I4
  loc_00417957: mov var_24, ax
  loc_0041795B: lea eax, var_60
  loc_0041795E: push eax
  loc_0041795F: lea ecx, var_5C
  loc_00417962: push ecx
  loc_00417963: lea edx, var_58
  loc_00417966: push edx
  loc_00417967: lea eax, var_54
  loc_0041796A: push eax
  loc_0041796B: lea ecx, var_50
  loc_0041796E: push ecx
  loc_0041796F: lea edx, var_4C
  loc_00417972: push edx
  loc_00417973: push 00000006h
  loc_00417975: call [00401180h] ; __vbaFreeStrList
  loc_0041797B: add esp, 0000001Ch
  loc_0041797E: lea eax, var_A8
  loc_00417984: push eax
  loc_00417985: lea ecx, var_98
  loc_0041798B: push ecx
  loc_0041798C: lea edx, var_88
  loc_00417992: push edx
  loc_00417993: lea eax, var_78
  loc_00417996: push eax
  loc_00417997: push 00000004h
  loc_00417999: call [00401038h] ; __vbaFreeVarList
  loc_0041799F: add esp, 00000014h
  loc_004179A2: mov var_4, 0000007Dh
  loc_004179A9: movsx ecx, var_24
  loc_004179AD: cmp ecx, 00000007h
  loc_004179B0: jnz 00417A16h
  loc_004179B2: mov var_4, 0000007Eh
  loc_004179B9: lea edx, var_78
  loc_004179BC: push edx
  loc_004179BD: mov eax, Me
  loc_004179C0: mov ecx, [eax]
  loc_004179C2: mov edx, Me
  loc_004179C5: push edx
  loc_004179C6: call [ecx+00000704h]
  loc_004179CC: mov var_1B8, eax
  loc_004179D2: cmp var_1B8, 00000000h
  loc_004179D9: jge 004179FEh
  loc_004179DB: push 00000704h
  loc_004179E0: push 0040579Ch ; "#]=VｫoyAｷ ;ﾑs：ﾚLabel12"
  loc_004179E5: mov eax, Me
  loc_004179E8: push eax
  loc_004179E9: mov ecx, var_1B8
  loc_004179EF: push ecx
  loc_004179F0: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004179F6: mov var_2FC, eax
  loc_004179FC: jmp 00417A08h
  loc_004179FE: mov var_2FC, 00000000h
  loc_00417A08: lea ecx, var_78
  loc_00417A0B: call [00401020h] ; __vbaFreeVar
  loc_00417A11: jmp 00418D07h
  loc_00417A16: mov var_4, 00000083h
  loc_00417A1D: lea edx, var_78
  loc_00417A20: push edx
  loc_00417A21: push 00423032h
  loc_00417A26: mov eax, Me
  loc_00417A29: mov ecx, [eax]
  loc_00417A2B: mov edx, Me
  loc_00417A2E: push edx
  loc_00417A2F: call [ecx+000006F8h]
  loc_00417A35: mov var_1B8, eax
  loc_00417A3B: cmp var_1B8, 00000000h
  loc_00417A42: jge 00417A67h
  loc_00417A44: push 000006F8h
  loc_00417A49: push 0040579Ch ; "#]=VｫoyAｷ ;ﾑs：ﾚLabel12"
  loc_00417A4E: mov eax, Me
  loc_00417A51: push eax
  loc_00417A52: mov ecx, var_1B8
  loc_00417A58: push ecx
  loc_00417A59: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00417A5F: mov var_300, eax
  loc_00417A65: jmp 00417A71h
  loc_00417A67: mov var_300, 00000000h
  loc_00417A71: lea ecx, var_78
  loc_00417A74: call [00401020h] ; __vbaFreeVar
  loc_00417A7A: mov var_4, 00000084h
  loc_00417A81: lea edx, var_1AC
  loc_00417A87: push edx
  loc_00417A88: mov eax, Me
  loc_00417A8B: mov ecx, [eax]
  loc_00417A8D: mov edx, Me
  loc_00417A90: push edx
  loc_00417A91: call [ecx+00000730h]
  loc_00417A97: mov var_4, 00000085h
  loc_00417A9E: call [004010A0h] ; rtcDoEvents
  loc_00417AA4: mov var_4, 00000086h
  loc_00417AAB: movsx eax, [00423032h]
  loc_00417AB2: test eax, eax
  loc_00417AB4: jnz 00418516h
  loc_00417ABA: mov var_4, 00000087h
  loc_00417AC1: mov ecx, Me
  loc_00417AC4: mov edx, [ecx]
  loc_00417AC6: mov eax, Me
  loc_00417AC9: push eax
  loc_00417ACA: call [edx+00000350h]
  loc_00417AD0: push eax
  loc_00417AD1: lea ecx, var_64
  loc_00417AD4: push ecx
  loc_00417AD5: call [00401080h] ; __vbaObjSet
  loc_00417ADB: mov var_1B8, eax
  loc_00417AE1: push 00406E08h ; "Change to Production Mode"
  loc_00417AE6: mov edx, var_1B8
  loc_00417AEC: mov eax, [edx]
  loc_00417AEE: mov ecx, var_1B8
  loc_00417AF4: push ecx
  loc_00417AF5: call [eax+00000054h]
  loc_00417AF8: fnclex
  loc_00417AFA: mov var_1BC, eax
  loc_00417B00: cmp var_1BC, 00000000h
  loc_00417B07: jge 00417B2Ch
  loc_00417B09: push 00000054h
  loc_00417B0B: push 00406128h
  loc_00417B10: mov edx, var_1B8
  loc_00417B16: push edx
  loc_00417B17: mov eax, var_1BC
  loc_00417B1D: push eax
  loc_00417B1E: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00417B24: mov var_304, eax
  loc_00417B2A: jmp 00417B36h
  loc_00417B2C: mov var_304, 00000000h
  loc_00417B36: lea ecx, var_64
  loc_00417B39: call [004011F0h] ; __vbaFreeObj
  loc_00417B3F: mov var_4, 00000088h
  loc_00417B46: lea ecx, var_78
  loc_00417B49: push ecx
  loc_00417B4A: call [004011E4h] ; rtcGetPresentDate
  loc_00417B50: mov var_120, 00407234h ; "mm dd yyyy hh:mm:ss AMPM"
  loc_00417B5A: mov var_128, 00000008h
  loc_00417B64: lea edx, var_128
  loc_00417B6A: lea ecx, var_88
  loc_00417B70: call [004011B4h] ; __vbaVarDup
  loc_00417B76: push 00000001h
  loc_00417B78: push 00000001h
  loc_00417B7A: lea edx, var_88
  loc_00417B80: push edx
  loc_00417B81: lea eax, var_78
  loc_00417B84: push eax
  loc_00417B85: lea ecx, var_98
  loc_00417B8B: push ecx
  loc_00417B8C: call [00401054h] ; rtcVarFromFormatVar
  loc_00417B92: lea edx, var_98
  loc_00417B98: push edx
  loc_00417B99: call [00401030h] ; __vbaStrVarMove
  loc_00417B9F: mov edx, eax
  loc_00417BA1: lea ecx, var_2C
  loc_00417BA4: call [004011D0h] ; __vbaStrMove
  loc_00417BAA: lea eax, var_98
  loc_00417BB0: push eax
  loc_00417BB1: lea ecx, var_88
  loc_00417BB7: push ecx
  loc_00417BB8: lea edx, var_78
  loc_00417BBB: push edx
  loc_00417BBC: push 00000003h
  loc_00417BBE: call [00401038h] ; __vbaFreeVarList
  loc_00417BC4: add esp, 00000010h
  loc_00417BC7: mov var_4, 00000089h
  loc_00417BCE: lea eax, var_4C
  loc_00417BD1: push eax
  loc_00417BD2: lea ecx, var_2C
  loc_00417BD5: push ecx
  loc_00417BD6: mov edx, Me
  loc_00417BD9: mov eax, [edx]
  loc_00417BDB: mov ecx, Me
  loc_00417BDE: push ecx
  loc_00417BDF: call [eax+00000728h]
  loc_00417BE5: mov edx, var_4C
  loc_00417BE8: mov var_21C, edx
  loc_00417BEE: mov var_4C, 00000000h
  loc_00417BF5: mov edx, var_21C
  loc_00417BFB: lea ecx, var_2C
  loc_00417BFE: call [004011D0h] ; __vbaStrMove
  loc_00417C04: mov var_4, 0000008Ah
  loc_00417C0B: mov eax, Me
  loc_00417C0E: mov ecx, [eax]
  loc_00417C10: mov edx, Me
  loc_00417C13: push edx
  loc_00417C14: call [ecx+0000037Ch]
  loc_00417C1A: push eax
  loc_00417C1B: lea eax, var_64
  loc_00417C1E: push eax
  loc_00417C1F: call [00401080h] ; __vbaObjSet
  loc_00417C25: mov var_1B8, eax
  loc_00417C2B: push 00405E08h ; "C:\ProbeData\"
  loc_00417C30: mov ecx, var_2C
  loc_00417C33: push ecx
  loc_00417C34: call [00401050h] ; __vbaStrCat
  loc_00417C3A: mov edx, eax
  loc_00417C3C: lea ecx, var_4C
  loc_00417C3F: call [004011D0h] ; __vbaStrMove
  loc_00417C45: push eax
  loc_00417C46: push 0040726Ch ; ".txt"
  loc_00417C4B: call [00401050h] ; __vbaStrCat
  loc_00417C51: mov edx, eax
  loc_00417C53: lea ecx, var_50
  loc_00417C56: call [004011D0h] ; __vbaStrMove
  loc_00417C5C: push eax
  loc_00417C5D: mov edx, var_1B8
  loc_00417C63: mov eax, [edx]
  loc_00417C65: mov ecx, var_1B8
  loc_00417C6B: push ecx
  loc_00417C6C: call [eax+000000A4h]
  loc_00417C72: fnclex
  loc_00417C74: mov var_1BC, eax
  loc_00417C7A: cmp var_1BC, 00000000h
  loc_00417C81: jge 00417CA9h
  loc_00417C83: push 000000A4h
  loc_00417C88: push 00405398h
  loc_00417C8D: mov edx, var_1B8
  loc_00417C93: push edx
  loc_00417C94: mov eax, var_1BC
  loc_00417C9A: push eax
  loc_00417C9B: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00417CA1: mov var_308, eax
  loc_00417CA7: jmp 00417CB3h
  loc_00417CA9: mov var_308, 00000000h
  loc_00417CB3: lea ecx, var_50
  loc_00417CB6: push ecx
  loc_00417CB7: lea edx, var_4C
  loc_00417CBA: push edx
  loc_00417CBB: push 00000002h
  loc_00417CBD: call [00401180h] ; __vbaFreeStrList
  loc_00417CC3: add esp, 0000000Ch
  loc_00417CC6: lea ecx, var_64
  loc_00417CC9: call [004011F0h] ; __vbaFreeObj
  loc_00417CCF: mov var_4, 0000008Bh
  loc_00417CD6: mov eax, Me
  loc_00417CD9: mov ecx, [eax]
  loc_00417CDB: mov edx, Me
  loc_00417CDE: push edx
  loc_00417CDF: call [ecx+00000380h]
  loc_00417CE5: push eax
  loc_00417CE6: lea eax, var_64
  loc_00417CE9: push eax
  loc_00417CEA: call [00401080h] ; __vbaObjSet
  loc_00417CF0: mov var_1B8, eax
  loc_00417CF6: mov ecx, 00000001h
  loc_00417CFB: call [004010ECh] ; __vbaI2I4
  loc_00417D01: push eax
  loc_00417D02: mov ecx, var_1B8
  loc_00417D08: mov edx, [ecx]
  loc_00417D0A: mov eax, var_1B8
  loc_00417D10: push eax
  loc_00417D11: call [edx+000000E4h]
  loc_00417D17: fnclex
  loc_00417D19: mov var_1BC, eax
  loc_00417D1F: cmp var_1BC, 00000000h
  loc_00417D26: jge 00417D4Eh
  loc_00417D28: push 000000E4h
  loc_00417D2D: push 00405354h
  loc_00417D32: mov ecx, var_1B8
  loc_00417D38: push ecx
  loc_00417D39: mov edx, var_1BC
  loc_00417D3F: push edx
  loc_00417D40: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00417D46: mov var_30C, eax
  loc_00417D4C: jmp 00417D58h
  loc_00417D4E: mov var_30C, 00000000h
  loc_00417D58: lea ecx, var_64
  loc_00417D5B: call [004011F0h] ; __vbaFreeObj
  loc_00417D61: mov var_4, 0000008Ch
  loc_00417D68: mov eax, Me
  loc_00417D6B: mov ecx, [eax]
  loc_00417D6D: mov edx, Me
  loc_00417D70: push edx
  loc_00417D71: call [ecx+00000738h]
  loc_00417D77: mov var_1B8, eax
  loc_00417D7D: cmp var_1B8, 00000000h
  loc_00417D84: jge 00417DA9h
  loc_00417D86: push 00000738h
  loc_00417D8B: push 0040579Ch ; "#]=VｫoyAｷ ;ﾑs：ﾚLabel12"
  loc_00417D90: mov eax, Me
  loc_00417D93: push eax
  loc_00417D94: mov ecx, var_1B8
  loc_00417D9A: push ecx
  loc_00417D9B: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00417DA1: mov var_310, eax
  loc_00417DA7: jmp 00417DB3h
  loc_00417DA9: mov var_310, 00000000h
  loc_00417DB3: mov var_4, 0000008Dh
  loc_00417DBA: mov edx, Me
  loc_00417DBD: mov eax, [edx]
  loc_00417DBF: mov ecx, Me
  loc_00417DC2: push ecx
  loc_00417DC3: call [eax+00000378h]
  loc_00417DC9: push eax
  loc_00417DCA: lea edx, var_64
  loc_00417DCD: push edx
  loc_00417DCE: call [00401080h] ; __vbaObjSet
  loc_00417DD4: mov var_1B8, eax
  loc_00417DDA: push FFFFFFFFh
  loc_00417DDC: mov eax, var_1B8
  loc_00417DE2: mov ecx, [eax]
  loc_00417DE4: mov edx, var_1B8
  loc_00417DEA: push edx
  loc_00417DEB: call [ecx+000000E4h]
  loc_00417DF1: fnclex
  loc_00417DF3: mov var_1BC, eax
  loc_00417DF9: cmp var_1BC, 00000000h
  loc_00417E00: jge 00417E28h
  loc_00417E02: push 000000E4h
  loc_00417E07: push 00405388h
  loc_00417E0C: mov eax, var_1B8
  loc_00417E12: push eax
  loc_00417E13: mov ecx, var_1BC
  loc_00417E19: push ecx
  loc_00417E1A: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00417E20: mov var_314, eax
  loc_00417E26: jmp 00417E32h
  loc_00417E28: mov var_314, 00000000h
  loc_00417E32: lea ecx, var_64
  loc_00417E35: call [004011F0h] ; __vbaFreeObj
  loc_00417E3B: mov var_4, 0000008Eh
  loc_00417E42: mov edx, Me
  loc_00417E45: mov eax, [edx]
  loc_00417E47: mov ecx, Me
  loc_00417E4A: push ecx
  loc_00417E4B: call [eax+00000370h]
  loc_00417E51: push eax
  loc_00417E52: lea edx, var_64
  loc_00417E55: push edx
  loc_00417E56: call [00401080h] ; __vbaObjSet
  loc_00417E5C: mov var_1B8, eax
  loc_00417E62: mov eax, var_1B8
  loc_00417E68: mov ecx, [eax]
  loc_00417E6A: mov edx, var_1B8
  loc_00417E70: push edx
  loc_00417E71: call [ecx+000001E8h]
  loc_00417E77: fnclex
  loc_00417E79: mov var_1BC, eax
  loc_00417E7F: cmp var_1BC, 00000000h
  loc_00417E86: jge 00417EAEh
  loc_00417E88: push 000001E8h
  loc_00417E8D: push 004055DCh
  loc_00417E92: mov eax, var_1B8
  loc_00417E98: push eax
  loc_00417E99: mov ecx, var_1BC
  loc_00417E9F: push ecx
  loc_00417EA0: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00417EA6: mov var_318, eax
  loc_00417EAC: jmp 00417EB8h
  loc_00417EAE: mov var_318, 00000000h
  loc_00417EB8: lea ecx, var_64
  loc_00417EBB: call [004011F0h] ; __vbaFreeObj
  loc_00417EC1: mov var_4, 0000008Fh
  loc_00417EC8: mov edx, Me
  loc_00417ECB: mov ecx, [edx+00000054h]
  loc_00417ECE: sub ecx, 00000001h
  loc_00417ED1: jo 00418DF3h
  loc_00417ED7: call [004010ECh] ; __vbaI2I4
  loc_00417EDD: mov var_204, ax
  loc_00417EE4: mov var_200, 0001h
  loc_00417EED: mov var_24, 0000h
  loc_00417EF3: jmp 00417F0Ah
  loc_00417EF5: mov ax, var_24
  loc_00417EF9: add ax, var_200
  loc_00417F00: jo 00418DF3h
  loc_00417F06: mov var_24, ax
  loc_00417F0A: mov cx, var_24
  loc_00417F0E: cmp cx, var_204
  loc_00417F15: jg 00418071h
  loc_00417F1B: mov var_4, 00000090h
  loc_00417F22: mov edx, Me
  loc_00417F25: mov eax, [edx]
  loc_00417F27: mov ecx, Me
  loc_00417F2A: push ecx
  loc_00417F2B: call [eax+00000370h]
  loc_00417F31: push eax
  loc_00417F32: lea edx, var_64
  loc_00417F35: push edx
  loc_00417F36: call [00401080h] ; __vbaObjSet
  loc_00417F3C: mov var_1BC, eax
  loc_00417F42: mov var_120, 80020004h
  loc_00417F4C: mov var_128, 0000000Ah
  loc_00417F56: mov eax, Me
  loc_00417F59: cmp [eax+0000004Ch], 00000000h
  loc_00417F5D: jz 00417FB8h
  loc_00417F5F: mov ecx, Me
  loc_00417F62: mov edx, [ecx+0000004Ch]
  loc_00417F65: cmp [edx], 0001h
  loc_00417F69: jnz 00417FB8h
  loc_00417F6B: movsx eax, var_24
  loc_00417F6F: mov ecx, Me
  loc_00417F72: mov edx, [ecx+0000004Ch]
  loc_00417F75: sub eax, [edx+00000014h]
  loc_00417F78: mov var_1B8, eax
  loc_00417F7E: mov eax, Me
  loc_00417F81: mov ecx, [eax+0000004Ch]
  loc_00417F84: mov edx, var_1B8
  loc_00417F8A: cmp edx, [ecx+00000010h]
  loc_00417F8D: jae 00417F9Bh
  loc_00417F8F: mov var_31C, 00000000h
  loc_00417F99: jmp 00417FA7h
  loc_00417F9B: call [004010D8h] ; __vbaGenerateBoundsError
  loc_00417FA1: mov var_31C, eax
  loc_00417FA7: mov eax, var_1B8
  loc_00417FAD: shl eax, 02h
  loc_00417FB0: mov var_320, eax
  loc_00417FB6: jmp 00417FC4h
  loc_00417FB8: call [004010D8h] ; __vbaGenerateBoundsError
  loc_00417FBE: mov var_320, eax
  loc_00417FC4: mov eax, 00000010h
  loc_00417FC9: call 00401AA0h ; __vbaChkstk
  loc_00417FCE: mov ecx, esp
  loc_00417FD0: mov edx, var_128
  loc_00417FD6: mov [ecx], edx
  loc_00417FD8: mov eax, var_124
  loc_00417FDE: mov [ecx+00000004h], eax
  loc_00417FE1: mov edx, var_120
  loc_00417FE7: mov [ecx+00000008h], edx
  loc_00417FEA: mov eax, var_11C
  loc_00417FF0: mov [ecx+0000000Ch], eax
  loc_00417FF3: mov ecx, Me
  loc_00417FF6: mov edx, [ecx+0000004Ch]
  loc_00417FF9: mov eax, [edx+0000000Ch]
  loc_00417FFC: mov ecx, var_320
  loc_00418002: mov edx, [eax+ecx]
  loc_00418005: push edx
  loc_00418006: mov eax, var_1BC
  loc_0041800C: mov ecx, [eax]
  loc_0041800E: mov edx, var_1BC
  loc_00418014: push edx
  loc_00418015: call [ecx+000001ECh]
  loc_0041801B: fnclex
  loc_0041801D: mov var_1C0, eax
  loc_00418023: cmp var_1C0, 00000000h
  loc_0041802A: jge 00418052h
  loc_0041802C: push 000001ECh
  loc_00418031: push 004055DCh
  loc_00418036: mov eax, var_1BC
  loc_0041803C: push eax
  loc_0041803D: mov ecx, var_1C0
  loc_00418043: push ecx
  loc_00418044: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041804A: mov var_324, eax
  loc_00418050: jmp 0041805Ch
  loc_00418052: mov var_324, 00000000h
  loc_0041805C: lea ecx, var_64
  loc_0041805F: call [004011F0h] ; __vbaFreeObj
  loc_00418065: mov var_4, 00000091h
  loc_0041806C: jmp 00417EF5h
  loc_00418071: mov var_4, 00000092h
  loc_00418078: mov edx, Me
  loc_0041807B: mov eax, [edx]
  loc_0041807D: mov ecx, Me
  loc_00418080: push ecx
  loc_00418081: call [eax+00000370h]
  loc_00418087: push eax
  loc_00418088: lea edx, var_64
  loc_0041808B: push edx
  loc_0041808C: call [00401080h] ; __vbaObjSet
  loc_00418092: mov var_1B8, eax
  loc_00418098: push 00000000h
  loc_0041809A: mov eax, var_1B8
  loc_004180A0: mov ecx, [eax]
  loc_004180A2: mov edx, var_1B8
  loc_004180A8: push edx
  loc_004180A9: call [ecx+000000F4h]
  loc_004180AF: fnclex
  loc_004180B1: mov var_1BC, eax
  loc_004180B7: cmp var_1BC, 00000000h
  loc_004180BE: jge 004180E6h
  loc_004180C0: push 000000F4h
  loc_004180C5: push 004055DCh
  loc_004180CA: mov eax, var_1B8
  loc_004180D0: push eax
  loc_004180D1: mov ecx, var_1BC
  loc_004180D7: push ecx
  loc_004180D8: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004180DE: mov var_328, eax
  loc_004180E4: jmp 004180F0h
  loc_004180E6: mov var_328, 00000000h
  loc_004180F0: lea ecx, var_64
  loc_004180F3: call [004011F0h] ; __vbaFreeObj
  loc_004180F9: mov var_4, 00000093h
  loc_00418100: call [004010A0h] ; rtcDoEvents
  loc_00418106: mov var_4, 00000094h
  loc_0041810D: cmp [00423010h], 00000000h
  loc_00418114: jnz 00418132h
  loc_00418116: push 00423010h
  loc_0041811B: push 004025D8h
  loc_00418120: call [00401168h] ; __vbaNew2
  loc_00418126: mov var_32C, 00423010h
  loc_00418130: jmp 0041813Ch
  loc_00418132: mov var_32C, 00423010h
  loc_0041813C: mov edx, var_32C
  loc_00418142: mov eax, [edx]
  loc_00418144: mov ecx, var_32C
  loc_0041814A: mov edx, [ecx]
  loc_0041814C: mov ecx, [edx]
  loc_0041814E: push eax
  loc_0041814F: call [ecx+00000308h]
  loc_00418155: push eax
  loc_00418156: lea edx, var_64
  loc_00418159: push edx
  loc_0041815A: call [00401080h] ; __vbaObjSet
  loc_00418160: mov var_1B8, eax
  loc_00418166: lea eax, var_4C
  loc_00418169: push eax
  loc_0041816A: mov ecx, var_1B8
  loc_00418170: mov edx, [ecx]
  loc_00418172: mov eax, var_1B8
  loc_00418178: push eax
  loc_00418179: call [edx+000000A0h]
  loc_0041817F: fnclex
  loc_00418181: mov var_1BC, eax
  loc_00418187: cmp var_1BC, 00000000h
  loc_0041818E: jge 004181B6h
  loc_00418190: push 000000A0h
  loc_00418195: push 00405398h
  loc_0041819A: mov ecx, var_1B8
  loc_004181A0: push ecx
  loc_004181A1: mov edx, var_1BC
  loc_004181A7: push edx
  loc_004181A8: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004181AE: mov var_330, eax
  loc_004181B4: jmp 004181C0h
  loc_004181B6: mov var_330, 00000000h
  loc_004181C0: mov eax, var_4C
  loc_004181C3: mov var_220, eax
  loc_004181C9: mov var_4C, 00000000h
  loc_004181D0: mov edx, var_220
  loc_004181D6: lea ecx, var_2C
  loc_004181D9: call [004011D0h] ; __vbaStrMove
  loc_004181DF: lea ecx, var_64
  loc_004181E2: call [004011F0h] ; __vbaFreeObj
  loc_004181E8: mov var_4, 00000095h
  loc_004181EF: mov ecx, var_2C
  loc_004181F2: push ecx
  loc_004181F3: push 00000000h
  loc_004181F5: call [004010DCh] ; __vbaStrCmp
  loc_004181FB: test eax, eax
  loc_004181FD: jnz 00418293h
  loc_00418203: mov var_4, 00000096h
  loc_0041820A: mov edx, Me
  loc_0041820D: mov eax, [edx]
  loc_0041820F: mov ecx, Me
  loc_00418212: push ecx
  loc_00418213: call [eax+00000364h]
  loc_00418219: push eax
  loc_0041821A: lea edx, var_64
  loc_0041821D: push edx
  loc_0041821E: call [00401080h] ; __vbaObjSet
  loc_00418224: mov var_1B8, eax
  loc_0041822A: push 004053ACh ; "The Wafer ID"
  loc_0041822F: mov eax, var_1B8
  loc_00418235: mov ecx, [eax]
  loc_00418237: mov edx, var_1B8
  loc_0041823D: push edx
  loc_0041823E: call [ecx+000000A4h]
  loc_00418244: fnclex
  loc_00418246: mov var_1BC, eax
  loc_0041824C: cmp var_1BC, 00000000h
  loc_00418253: jge 0041827Bh
  loc_00418255: push 000000A4h
  loc_0041825A: push 00405398h
  loc_0041825F: mov eax, var_1B8
  loc_00418265: push eax
  loc_00418266: mov ecx, var_1BC
  loc_0041826C: push ecx
  loc_0041826D: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00418273: mov var_334, eax
  loc_00418279: jmp 00418285h
  loc_0041827B: mov var_334, 00000000h
  loc_00418285: lea ecx, var_64
  loc_00418288: call [004011F0h] ; __vbaFreeObj
  loc_0041828E: jmp 0041831Dh
  loc_00418293: mov var_4, 00000098h
  loc_0041829A: mov edx, Me
  loc_0041829D: mov eax, [edx]
  loc_0041829F: mov ecx, Me
  loc_004182A2: push ecx
  loc_004182A3: call [eax+00000364h]
  loc_004182A9: push eax
  loc_004182AA: lea edx, var_64
  loc_004182AD: push edx
  loc_004182AE: call [00401080h] ; __vbaObjSet
  loc_004182B4: mov var_1B8, eax
  loc_004182BA: mov eax, var_2C
  loc_004182BD: push eax
  loc_004182BE: mov ecx, var_1B8
  loc_004182C4: mov edx, [ecx]
  loc_004182C6: mov eax, var_1B8
  loc_004182CC: push eax
  loc_004182CD: call [edx+000000A4h]
  loc_004182D3: fnclex
  loc_004182D5: mov var_1BC, eax
  loc_004182DB: cmp var_1BC, 00000000h
  loc_004182E2: jge 0041830Ah
  loc_004182E4: push 000000A4h
  loc_004182E9: push 00405398h
  loc_004182EE: mov ecx, var_1B8
  loc_004182F4: push ecx
  loc_004182F5: mov edx, var_1BC
  loc_004182FB: push edx
  loc_004182FC: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00418302: mov var_338, eax
  loc_00418308: jmp 00418314h
  loc_0041830A: mov var_338, 00000000h
  loc_00418314: lea ecx, var_64
  loc_00418317: call [004011F0h] ; __vbaFreeObj
  loc_0041831D: mov var_4, 0000009Ah
  loc_00418324: mov eax, Me
  loc_00418327: mov ecx, [eax]
  loc_00418329: mov edx, Me
  loc_0041832C: push edx
  loc_0041832D: call [ecx+00000304h]
  loc_00418333: push eax
  loc_00418334: lea eax, var_64
  loc_00418337: push eax
  loc_00418338: call [00401080h] ; __vbaObjSet
  loc_0041833E: mov var_1BC, eax
  loc_00418344: mov edx, 00406764h ; "MeterCurrentLimit"
  loc_00418349: lea ecx, var_4C
  loc_0041834C: call [00401178h] ; __vbaStrCopy
  loc_00418352: lea ecx, var_50
  loc_00418355: push ecx
  loc_00418356: lea edx, var_4C
  loc_00418359: push edx
  loc_0041835A: mov eax, var_48
  loc_0041835D: mov ecx, [eax]
  loc_0041835F: mov edx, var_48
  loc_00418362: push edx
  loc_00418363: call [ecx+0000002Ch]
  loc_00418366: fnclex
  loc_00418368: mov var_1B8, eax
  loc_0041836E: cmp var_1B8, 00000000h
  loc_00418375: jge 00418397h
  loc_00418377: push 0000002Ch
  loc_00418379: push 00405B8Ch
  loc_0041837E: mov eax, var_48
  loc_00418381: push eax
  loc_00418382: mov ecx, var_1B8
  loc_00418388: push ecx
  loc_00418389: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041838F: mov var_33C, eax
  loc_00418395: jmp 004183A1h
  loc_00418397: mov var_33C, 00000000h
  loc_004183A1: mov edx, var_50
  loc_004183A4: push edx
  loc_004183A5: mov eax, var_1BC
  loc_004183AB: mov ecx, [eax]
  loc_004183AD: mov edx, var_1BC
  loc_004183B3: push edx
  loc_004183B4: call [ecx+000000A4h]
  loc_004183BA: fnclex
  loc_004183BC: mov var_1C0, eax
  loc_004183C2: cmp var_1C0, 00000000h
  loc_004183C9: jge 004183F1h
  loc_004183CB: push 000000A4h
  loc_004183D0: push 00405398h
  loc_004183D5: mov eax, var_1BC
  loc_004183DB: push eax
  loc_004183DC: mov ecx, var_1C0
  loc_004183E2: push ecx
  loc_004183E3: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004183E9: mov var_340, eax
  loc_004183EF: jmp 004183FBh
  loc_004183F1: mov var_340, 00000000h
  loc_004183FB: lea edx, var_50
  loc_004183FE: push edx
  loc_004183FF: lea eax, var_4C
  loc_00418402: push eax
  loc_00418403: push 00000002h
  loc_00418405: call [00401180h] ; __vbaFreeStrList
  loc_0041840B: add esp, 0000000Ch
  loc_0041840E: lea ecx, var_64
  loc_00418411: call [004011F0h] ; __vbaFreeObj
  loc_00418417: mov var_4, 0000009Bh
  loc_0041841E: mov ecx, Me
  loc_00418421: mov edx, [ecx]
  loc_00418423: mov eax, Me
  loc_00418426: push eax
  loc_00418427: call [edx+00000308h]
  loc_0041842D: push eax
  loc_0041842E: lea ecx, var_64
  loc_00418431: push ecx
  loc_00418432: call [00401080h] ; __vbaObjSet
  loc_00418438: mov var_1BC, eax
  loc_0041843E: mov edx, 004060DCh ; "MeterRange"
  loc_00418443: lea ecx, var_4C
  loc_00418446: call [00401178h] ; __vbaStrCopy
  loc_0041844C: lea edx, var_50
  loc_0041844F: push edx
  loc_00418450: lea eax, var_4C
  loc_00418453: push eax
  loc_00418454: mov ecx, var_48
  loc_00418457: mov edx, [ecx]
  loc_00418459: mov eax, var_48
  loc_0041845C: push eax
  loc_0041845D: call [edx+0000002Ch]
  loc_00418460: fnclex
  loc_00418462: mov var_1B8, eax
  loc_00418468: cmp var_1B8, 00000000h
  loc_0041846F: jge 00418491h
  loc_00418471: push 0000002Ch
  loc_00418473: push 00405B8Ch
  loc_00418478: mov ecx, var_48
  loc_0041847B: push ecx
  loc_0041847C: mov edx, var_1B8
  loc_00418482: push edx
  loc_00418483: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00418489: mov var_344, eax
  loc_0041848F: jmp 0041849Bh
  loc_00418491: mov var_344, 00000000h
  loc_0041849B: mov eax, var_50
  loc_0041849E: push eax
  loc_0041849F: mov ecx, var_1BC
  loc_004184A5: mov edx, [ecx]
  loc_004184A7: mov eax, var_1BC
  loc_004184AD: push eax
  loc_004184AE: call [edx+000000A4h]
  loc_004184B4: fnclex
  loc_004184B6: mov var_1C0, eax
  loc_004184BC: cmp var_1C0, 00000000h
  loc_004184C3: jge 004184EBh
  loc_004184C5: push 000000A4h
  loc_004184CA: push 00405398h
  loc_004184CF: mov ecx, var_1BC
  loc_004184D5: push ecx
  loc_004184D6: mov edx, var_1C0
  loc_004184DC: push edx
  loc_004184DD: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004184E3: mov var_348, eax
  loc_004184E9: jmp 004184F5h
  loc_004184EB: mov var_348, 00000000h
  loc_004184F5: lea eax, var_50
  loc_004184F8: push eax
  loc_004184F9: lea ecx, var_4C
  loc_004184FC: push ecx
  loc_004184FD: push 00000002h
  loc_004184FF: call [00401180h] ; __vbaFreeStrList
  loc_00418505: add esp, 0000000Ch
  loc_00418508: lea ecx, var_64
  loc_0041850B: call [004011F0h] ; __vbaFreeObj
  loc_00418511: jmp 0041859Bh
  loc_00418516: mov var_4, 0000009Dh
  loc_0041851D: mov edx, Me
  loc_00418520: mov eax, [edx]
  loc_00418522: mov ecx, Me
  loc_00418525: push ecx
  loc_00418526: call [eax+00000350h]
  loc_0041852C: push eax
  loc_0041852D: lea edx, var_64
  loc_00418530: push edx
  loc_00418531: call [00401080h] ; __vbaObjSet
  loc_00418537: mov var_1B8, eax
  loc_0041853D: push 00406DCCh ; "Change to Engineering Mode"
  loc_00418542: mov eax, var_1B8
  loc_00418548: mov ecx, [eax]
  loc_0041854A: mov edx, var_1B8
  loc_00418550: push edx
  loc_00418551: call [ecx+00000054h]
  loc_00418554: fnclex
  loc_00418556: mov var_1BC, eax
  loc_0041855C: cmp var_1BC, 00000000h
  loc_00418563: jge 00418588h
  loc_00418565: push 00000054h
  loc_00418567: push 00406128h
  loc_0041856C: mov eax, var_1B8
  loc_00418572: push eax
  loc_00418573: mov ecx, var_1BC
  loc_00418579: push ecx
  loc_0041857A: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00418580: mov var_34C, eax
  loc_00418586: jmp 00418592h
  loc_00418588: mov var_34C, 00000000h
  loc_00418592: lea ecx, var_64
  loc_00418595: call [004011F0h] ; __vbaFreeObj
  loc_0041859B: mov var_4, 0000009Fh
  loc_004185A2: movsx edx, [00423034h]
  loc_004185A9: test edx, edx
  loc_004185AB: jz 00418643h
  loc_004185B1: mov var_4, 000000A0h
  loc_004185B8: mov eax, Me
  loc_004185BB: mov ecx, [eax]
  loc_004185BD: mov edx, Me
  loc_004185C0: push edx
  loc_004185C1: call [ecx+00000358h]
  loc_004185C7: push eax
  loc_004185C8: lea eax, var_64
  loc_004185CB: push eax
  loc_004185CC: call [00401080h] ; __vbaObjSet
  loc_004185D2: mov var_1B8, eax
  loc_004185D8: mov ecx, 00000001h
  loc_004185DD: call [004010ECh] ; __vbaI2I4
  loc_004185E3: push eax
  loc_004185E4: mov ecx, var_1B8
  loc_004185EA: mov edx, [ecx]
  loc_004185EC: mov eax, var_1B8
  loc_004185F2: push eax
  loc_004185F3: call [edx+000000E4h]
  loc_004185F9: fnclex
  loc_004185FB: mov var_1BC, eax
  loc_00418601: cmp var_1BC, 00000000h
  loc_00418608: jge 00418630h
  loc_0041860A: push 000000E4h
  loc_0041860F: push 00405354h
  loc_00418614: mov ecx, var_1B8
  loc_0041861A: push ecx
  loc_0041861B: mov edx, var_1BC
  loc_00418621: push edx
  loc_00418622: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00418628: mov var_350, eax
  loc_0041862E: jmp 0041863Ah
  loc_00418630: mov var_350, 00000000h
  loc_0041863A: lea ecx, var_64
  loc_0041863D: call [004011F0h] ; __vbaFreeObj
  loc_00418643: mov var_4, 000000A2h
  loc_0041864A: push 00405B8Ch
  loc_0041864F: push 00000000h
  loc_00418651: call [004011D4h] ; __vbaCastObj
  loc_00418657: push eax
  loc_00418658: lea eax, var_48
  loc_0041865B: push eax
  loc_0041865C: call [00401080h] ; __vbaObjSet
  loc_00418662: mov var_4, 000000A3h
  loc_00418669: mov ecx, Me
  loc_0041866C: mov edx, [ecx]
  loc_0041866E: mov eax, Me
  loc_00418671: push eax
  loc_00418672: call [edx+00000394h]
  loc_00418678: push eax
  loc_00418679: lea ecx, var_64
  loc_0041867C: push ecx
  loc_0041867D: call [00401080h] ; __vbaObjSet
  loc_00418683: mov var_1B8, eax
  loc_00418689: push 00000000h
  loc_0041868B: mov edx, var_1B8
  loc_00418691: mov eax, [edx]
  loc_00418693: mov ecx, var_1B8
  loc_00418699: push ecx
  loc_0041869A: call [eax+0000005Ch]
  loc_0041869D: fnclex
  loc_0041869F: mov var_1BC, eax
  loc_004186A5: cmp var_1BC, 00000000h
  loc_004186AC: jge 004186D1h
  loc_004186AE: push 0000005Ch
  loc_004186B0: push 004056F4h
  loc_004186B5: mov edx, var_1B8
  loc_004186BB: push edx
  loc_004186BC: mov eax, var_1BC
  loc_004186C2: push eax
  loc_004186C3: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004186C9: mov var_354, eax
  loc_004186CF: jmp 004186DBh
  loc_004186D1: mov var_354, 00000000h
  loc_004186DB: lea ecx, var_64
  loc_004186DE: call [004011F0h] ; __vbaFreeObj
  loc_004186E4: mov var_4, 000000A4h
  loc_004186EB: mov ecx, Me
  loc_004186EE: mov edx, [ecx]
  loc_004186F0: mov eax, Me
  loc_004186F3: push eax
  loc_004186F4: call [edx+0000039Ch]
  loc_004186FA: push eax
  loc_004186FB: lea ecx, var_64
  loc_004186FE: push ecx
  loc_004186FF: call [00401080h] ; __vbaObjSet
  loc_00418705: mov var_1B8, eax
  loc_0041870B: push 00406380h ; "Ready"
  loc_00418710: mov edx, var_1B8
  loc_00418716: mov eax, [edx]
  loc_00418718: mov ecx, var_1B8
  loc_0041871E: push ecx
  loc_0041871F: call [eax+00000054h]
  loc_00418722: fnclex
  loc_00418724: mov var_1BC, eax
  loc_0041872A: cmp var_1BC, 00000000h
  loc_00418731: jge 00418756h
  loc_00418733: push 00000054h
  loc_00418735: push 0040575Ch
  loc_0041873A: mov edx, var_1B8
  loc_00418740: push edx
  loc_00418741: mov eax, var_1BC
  loc_00418747: push eax
  loc_00418748: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041874E: mov var_358, eax
  loc_00418754: jmp 00418760h
  loc_00418756: mov var_358, 00000000h
  loc_00418760: lea ecx, var_64
  loc_00418763: call [004011F0h] ; __vbaFreeObj
  loc_00418769: mov var_4, 000000A5h
  loc_00418770: cmp [00423010h], 00000000h
  loc_00418777: jnz 00418795h
  loc_00418779: push 00423010h
  loc_0041877E: push 004025D8h
  loc_00418783: call [00401168h] ; __vbaNew2
  loc_00418789: mov var_35C, 00423010h
  loc_00418793: jmp 0041879Fh
  loc_00418795: mov var_35C, 00423010h
  loc_0041879F: mov ecx, var_35C
  loc_004187A5: mov edx, [ecx]
  loc_004187A7: mov eax, var_35C
  loc_004187AD: mov ecx, [eax]
  loc_004187AF: mov eax, [ecx]
  loc_004187B1: push edx
  loc_004187B2: call [eax+00000300h]
  loc_004187B8: push eax
  loc_004187B9: lea ecx, var_64
  loc_004187BC: push ecx
  loc_004187BD: call [00401080h] ; __vbaObjSet
  loc_004187C3: mov var_1B8, eax
  loc_004187C9: push 00000000h
  loc_004187CB: mov edx, var_1B8
  loc_004187D1: mov eax, [edx]
  loc_004187D3: mov ecx, var_1B8
  loc_004187D9: push ecx
  loc_004187DA: call [eax+0000005Ch]
  loc_004187DD: fnclex
  loc_004187DF: mov var_1BC, eax
  loc_004187E5: cmp var_1BC, 00000000h
  loc_004187EC: jge 00418811h
  loc_004187EE: push 0000005Ch
  loc_004187F0: push 004056F4h
  loc_004187F5: mov edx, var_1B8
  loc_004187FB: push edx
  loc_004187FC: mov eax, var_1BC
  loc_00418802: push eax
  loc_00418803: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00418809: mov var_360, eax
  loc_0041880F: jmp 0041881Bh
  loc_00418811: mov var_360, 00000000h
  loc_0041881B: lea ecx, var_64
  loc_0041881E: call [004011F0h] ; __vbaFreeObj
  loc_00418824: mov var_4, 000000A6h
  loc_0041882B: cmp [00423010h], 00000000h
  loc_00418832: jnz 00418850h
  loc_00418834: push 00423010h
  loc_00418839: push 004025D8h
  loc_0041883E: call [00401168h] ; __vbaNew2
  loc_00418844: mov var_364, 00423010h
  loc_0041884E: jmp 0041885Ah
  loc_00418850: mov var_364, 00423010h
  loc_0041885A: mov ecx, var_364
  loc_00418860: mov edx, [ecx]
  loc_00418862: mov eax, var_364
  loc_00418868: mov ecx, [eax]
  loc_0041886A: mov eax, [ecx]
  loc_0041886C: push edx
  loc_0041886D: call [eax+0000032Ch]
  loc_00418873: push eax
  loc_00418874: lea ecx, var_64
  loc_00418877: push ecx
  loc_00418878: call [00401080h] ; __vbaObjSet
  loc_0041887E: mov var_1B8, eax
  loc_00418884: push 00000000h
  loc_00418886: mov edx, var_1B8
  loc_0041888C: mov eax, [edx]
  loc_0041888E: mov ecx, var_1B8
  loc_00418894: push ecx
  loc_00418895: call [eax+00000054h]
  loc_00418898: fnclex
  loc_0041889A: mov var_1BC, eax
  loc_004188A0: cmp var_1BC, 00000000h
  loc_004188A7: jge 004188CCh
  loc_004188A9: push 00000054h
  loc_004188AB: push 0040575Ch
  loc_004188B0: mov edx, var_1B8
  loc_004188B6: push edx
  loc_004188B7: mov eax, var_1BC
  loc_004188BD: push eax
  loc_004188BE: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004188C4: mov var_368, eax
  loc_004188CA: jmp 004188D6h
  loc_004188CC: mov var_368, 00000000h
  loc_004188D6: lea ecx, var_64
  loc_004188D9: call [004011F0h] ; __vbaFreeObj
  loc_004188DF: mov var_4, 000000A7h
  loc_004188E6: cmp [00423010h], 00000000h
  loc_004188ED: jnz 0041890Bh
  loc_004188EF: push 00423010h
  loc_004188F4: push 004025D8h
  loc_004188F9: call [00401168h] ; __vbaNew2
  loc_004188FF: mov var_36C, 00423010h
  loc_00418909: jmp 00418915h
  loc_0041890B: mov var_36C, 00423010h
  loc_00418915: mov ecx, var_36C
  loc_0041891B: mov edx, [ecx]
  loc_0041891D: mov var_1B8, edx
  loc_00418923: mov eax, var_1B8
  loc_00418929: mov ecx, [eax]
  loc_0041892B: mov edx, var_1B8
  loc_00418931: push edx
  loc_00418932: call [ecx+000002B4h]
  loc_00418938: fnclex
  loc_0041893A: mov var_1BC, eax
  loc_00418940: cmp var_1BC, 00000000h
  loc_00418947: jge 0041896Fh
  loc_00418949: push 000002B4h
  loc_0041894E: push 00405120h
  loc_00418953: mov eax, var_1B8
  loc_00418959: push eax
  loc_0041895A: mov ecx, var_1BC
  loc_00418960: push ecx
  loc_00418961: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00418967: mov var_370, eax
  loc_0041896D: jmp 00418979h
  loc_0041896F: mov var_370, 00000000h
  loc_00418979: mov var_4, 000000A8h
  loc_00418980: push 00000000h
  loc_00418982: mov edx, Me
  loc_00418985: mov eax, [edx]
  loc_00418987: mov ecx, Me
  loc_0041898A: push ecx
  loc_0041898B: call [eax+000000A4h]
  loc_00418991: fnclex
  loc_00418993: mov var_1B8, eax
  loc_00418999: cmp var_1B8, 00000000h
  loc_004189A0: jge 004189C5h
  loc_004189A2: push 000000A4h
  loc_004189A7: push 0040576Ch
  loc_004189AC: mov edx, Me
  loc_004189AF: push edx
  loc_004189B0: mov eax, var_1B8
  loc_004189B6: push eax
  loc_004189B7: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004189BD: mov var_374, eax
  loc_004189C3: jmp 004189CFh
  loc_004189C5: mov var_374, 00000000h
  loc_004189CF: jmp 00418D07h
  loc_004189D4: mov var_4, 000000ABh
  loc_004189DB: call [00401190h] ; rtcErrObj
  loc_004189E1: push eax
  loc_004189E2: lea ecx, var_64
  loc_004189E5: push ecx
  loc_004189E6: call [00401080h] ; __vbaObjSet
  loc_004189EC: mov var_1B8, eax
  loc_004189F2: lea edx, var_1B4
  loc_004189F8: push edx
  loc_004189F9: mov eax, var_1B8
  loc_004189FF: mov ecx, [eax]
  loc_00418A01: mov edx, var_1B8
  loc_00418A07: push edx
  loc_00418A08: call [ecx+0000001Ch]
  loc_00418A0B: fnclex
  loc_00418A0D: mov var_1BC, eax
  loc_00418A13: cmp var_1BC, 00000000h
  loc_00418A1A: jge 00418A3Fh
  loc_00418A1C: push 0000001Ch
  loc_00418A1E: push 00406F64h
  loc_00418A23: mov eax, var_1B8
  loc_00418A29: push eax
  loc_00418A2A: mov ecx, var_1BC
  loc_00418A30: push ecx
  loc_00418A31: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00418A37: mov var_378, eax
  loc_00418A3D: jmp 00418A49h
  loc_00418A3F: mov var_378, 00000000h
  loc_00418A49: xor edx, edx
  loc_00418A4B: cmp var_1B4, 0000003Eh
  loc_00418A52: setz dl
  loc_00418A55: neg edx
  loc_00418A57: mov var_1C0, dx
  loc_00418A5E: lea ecx, var_64
  loc_00418A61: call [004011F0h] ; __vbaFreeObj
  loc_00418A67: movsx eax, var_1C0
  loc_00418A6E: test eax, eax
  loc_00418A70: jz 00418AE8h
  loc_00418A72: mov var_4, 000000ACh
  loc_00418A79: call [00401190h] ; rtcErrObj
  loc_00418A7F: push eax
  loc_00418A80: lea ecx, var_64
  loc_00418A83: push ecx
  loc_00418A84: call [00401080h] ; __vbaObjSet
  loc_00418A8A: mov var_37C, eax
  loc_00418A90: mov edx, var_37C
  loc_00418A96: mov eax, [edx]
  loc_00418A98: mov ecx, var_37C
  loc_00418A9E: push ecx
  loc_00418A9F: call [eax+00000048h]
  loc_00418AA2: lea ecx, var_64
  loc_00418AA5: call [004011F0h] ; __vbaFreeObj
  loc_00418AAB: mov var_4, 000000ADh
  loc_00418AB2: mov ecx, var_30
  loc_00418AB5: call [004010ECh] ; __vbaI2I4
  loc_00418ABB: push eax
  loc_00418ABC: call [004010CCh] ; __vbaFileClose
  loc_00418AC2: mov var_4, 000000AEh
  loc_00418AC9: call [004010A0h] ; rtcDoEvents
  loc_00418ACF: mov var_4, 000000AFh
  loc_00418AD6: push 00000000h
  loc_00418AD8: call [0040104Ch] ; __vbaResume
  loc_00418ADE: jmp 0041546Dh
  loc_00418AE3: jmp 00418D07h
  loc_00418AE8: mov var_4, 000000B1h
  loc_00418AEF: call [00401190h] ; rtcErrObj
  loc_00418AF5: push eax
  loc_00418AF6: lea edx, var_64
  loc_00418AF9: push edx
  loc_00418AFA: call [00401080h] ; __vbaObjSet
  loc_00418B00: mov var_1B8, eax
  loc_00418B06: lea eax, var_1B4
  loc_00418B0C: push eax
  loc_00418B0D: mov ecx, var_1B8
  loc_00418B13: mov edx, [ecx]
  loc_00418B15: mov eax, var_1B8
  loc_00418B1B: push eax
  loc_00418B1C: call [edx+0000001Ch]
  loc_00418B1F: fnclex
  loc_00418B21: mov var_1BC, eax
  loc_00418B27: cmp var_1BC, 00000000h
  loc_00418B2E: jge 00418B53h
  loc_00418B30: push 0000001Ch
  loc_00418B32: push 00406F64h
  loc_00418B37: mov ecx, var_1B8
  loc_00418B3D: push ecx
  loc_00418B3E: mov edx, var_1BC
  loc_00418B44: push edx
  loc_00418B45: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00418B4B: mov var_380, eax
  loc_00418B51: jmp 00418B5Dh
  loc_00418B53: mov var_380, 00000000h
  loc_00418B5D: call [00401190h] ; rtcErrObj
  loc_00418B63: push eax
  loc_00418B64: lea eax, var_68
  loc_00418B67: push eax
  loc_00418B68: call [00401080h] ; __vbaObjSet
  loc_00418B6E: mov var_1C0, eax
  loc_00418B74: lea ecx, var_54
  loc_00418B77: push ecx
  loc_00418B78: mov edx, var_1C0
  loc_00418B7E: mov eax, [edx]
  loc_00418B80: mov ecx, var_1C0
  loc_00418B86: push ecx
  loc_00418B87: call [eax+0000002Ch]
  loc_00418B8A: fnclex
  loc_00418B8C: mov var_1C4, eax
  loc_00418B92: cmp var_1C4, 00000000h
  loc_00418B99: jge 00418BBEh
  loc_00418B9B: push 0000002Ch
  loc_00418B9D: push 00406F64h
  loc_00418BA2: mov edx, var_1C0
  loc_00418BA8: push edx
  loc_00418BA9: mov eax, var_1C4
  loc_00418BAF: push eax
  loc_00418BB0: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00418BB6: mov var_384, eax
  loc_00418BBC: jmp 00418BC8h
  loc_00418BBE: mov var_384, 00000000h
  loc_00418BC8: mov var_A0, 80020004h
  loc_00418BD2: mov var_A8, 0000000Ah
  loc_00418BDC: mov var_90, 80020004h
  loc_00418BE6: mov var_98, 0000000Ah
  loc_00418BF0: mov var_120, 004050E8h ; "IMT LampElectrical Probing"
  loc_00418BFA: mov var_128, 00000008h
  loc_00418C04: lea edx, var_128
  loc_00418C0A: lea ecx, var_88
  loc_00418C10: call [004011B4h] ; __vbaVarDup
  loc_00418C16: push 00407434h ; "Error "
  loc_00418C1B: mov ecx, var_1B4
  loc_00418C21: push ecx
  loc_00418C22: call [00401018h] ; __vbaStrI4
  loc_00418C28: mov edx, eax
  loc_00418C2A: lea ecx, var_4C
  loc_00418C2D: call [004011D0h] ; __vbaStrMove
  loc_00418C33: push eax
  loc_00418C34: call [00401050h] ; __vbaStrCat
  loc_00418C3A: mov edx, eax
  loc_00418C3C: lea ecx, var_50
  loc_00418C3F: call [004011D0h] ; __vbaStrMove
  loc_00418C45: push eax
  loc_00418C46: push 00407448h
  loc_00418C4B: call [00401050h] ; __vbaStrCat
  loc_00418C51: mov edx, eax
  loc_00418C53: lea ecx, var_58
  loc_00418C56: call [004011D0h] ; __vbaStrMove
  loc_00418C5C: push eax
  loc_00418C5D: mov edx, var_54
  loc_00418C60: push edx
  loc_00418C61: call [00401050h] ; __vbaStrCat
  loc_00418C67: mov var_70, eax
  loc_00418C6A: mov var_78, 00000008h
  loc_00418C71: lea eax, var_A8
  loc_00418C77: push eax
  loc_00418C78: lea ecx, var_98
  loc_00418C7E: push ecx
  loc_00418C7F: lea edx, var_88
  loc_00418C85: push edx
  loc_00418C86: push 00000010h
  loc_00418C88: lea eax, var_78
  loc_00418C8B: push eax
  loc_00418C8C: call [00401084h] ; rtcMsgBox
  loc_00418C92: lea ecx, var_54
  loc_00418C95: push ecx
  loc_00418C96: lea edx, var_58
  loc_00418C99: push edx
  loc_00418C9A: lea eax, var_50
  loc_00418C9D: push eax
  loc_00418C9E: lea ecx, var_4C
  loc_00418CA1: push ecx
  loc_00418CA2: push 00000004h
  loc_00418CA4: call [00401180h] ; __vbaFreeStrList
  loc_00418CAA: add esp, 00000014h
  loc_00418CAD: lea edx, var_68
  loc_00418CB0: push edx
  loc_00418CB1: lea eax, var_64
  loc_00418CB4: push eax
  loc_00418CB5: push 00000002h
  loc_00418CB7: call [00401040h] ; __vbaFreeObjList
  loc_00418CBD: add esp, 0000000Ch
  loc_00418CC0: lea ecx, var_A8
  loc_00418CC6: push ecx
  loc_00418CC7: lea edx, var_98
  loc_00418CCD: push edx
  loc_00418CCE: lea eax, var_88
  loc_00418CD4: push eax
  loc_00418CD5: lea ecx, var_78
  loc_00418CD8: push ecx
  loc_00418CD9: push 00000004h
  loc_00418CDB: call [00401038h] ; __vbaFreeVarList
  loc_00418CE1: add esp, 00000014h
  loc_00418CE4: mov var_4, 000000B2h
  loc_00418CEB: mov ecx, var_30
  loc_00418CEE: call [004010ECh] ; __vbaI2I4
  loc_00418CF4: push eax
  loc_00418CF5: call [004010CCh] ; __vbaFileClose
  loc_00418CFB: mov var_4, 000000B3h
  loc_00418D02: call 0041ECE0h
  loc_00418D07: call [00401074h] ; __vbaExitProc
  loc_00418D0D: push 00418DD1h
  loc_00418D12: jmp 00418DA3h
  loc_00418D17: lea edx, var_60
  loc_00418D1A: push edx
  loc_00418D1B: lea eax, var_5C
  loc_00418D1E: push eax
  loc_00418D1F: lea ecx, var_58
  loc_00418D22: push ecx
  loc_00418D23: lea edx, var_54
  loc_00418D26: push edx
  loc_00418D27: lea eax, var_50
  loc_00418D2A: push eax
  loc_00418D2B: lea ecx, var_4C
  loc_00418D2E: push ecx
  loc_00418D2F: push 00000006h
  loc_00418D31: call [00401180h] ; __vbaFreeStrList
  loc_00418D37: add esp, 0000001Ch
  loc_00418D3A: lea edx, var_68
  loc_00418D3D: push edx
  loc_00418D3E: lea eax, var_64
  loc_00418D41: push eax
  loc_00418D42: push 00000002h
  loc_00418D44: call [00401040h] ; __vbaFreeObjList
  loc_00418D4A: add esp, 0000000Ch
  loc_00418D4D: lea ecx, var_118
  loc_00418D53: push ecx
  loc_00418D54: lea edx, var_108
  loc_00418D5A: push edx
  loc_00418D5B: lea eax, var_F8
  loc_00418D61: push eax
  loc_00418D62: lea ecx, var_E8
  loc_00418D68: push ecx
  loc_00418D69: lea edx, var_D8
  loc_00418D6F: push edx
  loc_00418D70: lea eax, var_C8
  loc_00418D76: push eax
  loc_00418D77: lea ecx, var_B8
  loc_00418D7D: push ecx
  loc_00418D7E: lea edx, var_A8
  loc_00418D84: push edx
  loc_00418D85: lea eax, var_98
  loc_00418D8B: push eax
  loc_00418D8C: lea ecx, var_88
  loc_00418D92: push ecx
  loc_00418D93: lea edx, var_78
  loc_00418D96: push edx
  loc_00418D97: push 0000000Bh
  loc_00418D99: call [00401038h] ; __vbaFreeVarList
  loc_00418D9F: add esp, 00000030h
  loc_00418DA2: ret
  loc_00418DA3: lea ecx, var_28
  loc_00418DA6: call [004011F4h] ; __vbaFreeStr
  loc_00418DAC: lea ecx, var_2C
  loc_00418DAF: call [004011F4h] ; __vbaFreeStr
  loc_00418DB5: lea ecx, var_40
  loc_00418DB8: call [00401020h] ; __vbaFreeVar
  loc_00418DBE: lea ecx, var_44
  loc_00418DC1: call [004011F0h] ; __vbaFreeObj
  loc_00418DC7: lea ecx, var_48
  loc_00418DCA: call [004011F0h] ; __vbaFreeObj
  loc_00418DD0: ret
  loc_00418DD1: mov eax, Me
  loc_00418DD4: mov ecx, [eax]
  loc_00418DD6: mov edx, Me
  loc_00418DD9: push edx
  loc_00418DDA: call [ecx+00000008h]
  loc_00418DDD: mov eax, var_10
  loc_00418DE0: mov ecx, var_20
  loc_00418DE3: mov fs:[00000000h], ecx
  loc_00418DEA: pop edi
  loc_00418DEB: pop esi
  loc_00418DEC: pop ebx
  loc_00418DED: mov esp, ebp
  loc_00418DEF: pop ebp
  loc_00418DF0: retn 0004h
End Sub

Private Sub Form_Unload(Cancel As Integer) '418E00
  loc_00418E00: push ebp
  loc_00418E01: mov ebp, esp
  loc_00418E03: sub esp, 0000000Ch
  loc_00418E06: push 00401AA6h ; __vbaExceptHandler
  loc_00418E0B: mov eax, fs:[00000000h]
  loc_00418E11: push eax
  loc_00418E12: mov fs:[00000000h], esp
  loc_00418E19: sub esp, 00000020h
  loc_00418E1C: push ebx
  loc_00418E1D: push esi
  loc_00418E1E: push edi
  loc_00418E1F: mov var_C, esp
  loc_00418E22: mov var_8, 004015C8h
  loc_00418E29: mov esi, Me
  loc_00418E2C: mov eax, esi
  loc_00418E2E: and eax, 00000001h
  loc_00418E31: mov var_4, eax
  loc_00418E34: and esi, FFFFFFFEh
  loc_00418E37: push esi
  loc_00418E38: mov Me, esi
  loc_00418E3B: mov ecx, [esi]
  loc_00418E3D: call [ecx+00000004h]
  loc_00418E40: mov edx, [esi]
  loc_00418E42: xor edi, edi
  loc_00418E44: push esi
  loc_00418E45: mov var_18, edi
  loc_00418E48: mov var_1C, edi
  loc_00418E4B: mov var_20, edi
  loc_00418E4E: call [edx+000002FCh]
  loc_00418E54: push eax
  loc_00418E55: lea eax, var_1C
  loc_00418E58: push eax
  loc_00418E59: call [00401080h] ; __vbaObjSet
  loc_00418E5F: mov esi, eax
  loc_00418E61: lea edx, var_20
  loc_00418E64: push edx
  loc_00418E65: push esi
  loc_00418E66: mov ecx, [esi]
  loc_00418E68: call [ecx+000000E0h]
  loc_00418E6E: cmp eax, edi
  loc_00418E70: fnclex
  loc_00418E72: jge 00418E86h
  loc_00418E74: push 000000E0h
  loc_00418E79: push 00405354h
  loc_00418E7E: push esi
  loc_00418E7F: push eax
  loc_00418E80: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00418E86: xor eax, eax
  loc_00418E88: cmp var_20, 0001h
  loc_00418E8D: lea ecx, var_1C
  loc_00418E90: setz al
  loc_00418E93: neg eax
  loc_00418E95: mov esi, eax
  loc_00418E97: call [004011F0h] ; __vbaFreeObj
  loc_00418E9D: cmp si, di
  loc_00418EA0: mov edx, 00406FF4h ; "True"
  loc_00418EA5: jnz 00418EACh
  loc_00418EA7: mov edx, 00406CF8h ; "False"
  loc_00418EAC: lea ecx, var_18
  loc_00418EAF: call [00401178h] ; __vbaStrCopy
  loc_00418EB5: mov ecx, var_18
  loc_00418EB8: push ecx
  loc_00418EB9: push 00406FD0h ; "FlushActivated"
  loc_00418EBE: push 00406FB8h ; "Settings"
  loc_00418EC3: push 00406F94h ; "LampElectrical"
  loc_00418EC8: call [00401008h] ; rtcSaveSetting
  loc_00418ECE: call 0041ECE0h
  loc_00418ED3: mov var_4, edi
  loc_00418ED6: push 00418EF1h
  loc_00418EDB: jmp 00418EE7h
  loc_00418EDD: lea ecx, var_1C
  loc_00418EE0: call [004011F0h] ; __vbaFreeObj
  loc_00418EE6: ret
  loc_00418EE7: lea ecx, var_18
  loc_00418EEA: call [004011F4h] ; __vbaFreeStr
  loc_00418EF0: ret
  loc_00418EF1: mov eax, Me
  loc_00418EF4: push eax
  loc_00418EF5: mov edx, [eax]
  loc_00418EF7: call [edx+00000008h]
  loc_00418EFA: mov eax, var_4
  loc_00418EFD: mov ecx, var_14
  loc_00418F00: pop edi
  loc_00418F01: pop esi
  loc_00418F02: mov fs:[00000000h], ecx
  loc_00418F09: pop ebx
  loc_00418F0A: mov esp, ebp
  loc_00418F0C: pop ebp
  loc_00418F0D: retn 0008h
End Sub

Public Function SetUpRunTimeControls(IsFull) '419770
  loc_00419770: push ebp
  loc_00419771: mov ebp, esp
  loc_00419773: sub esp, 0000000Ch
  loc_00419776: push 00401AA6h ; __vbaExceptHandler
  loc_0041977B: mov eax, fs:[00000000h]
  loc_00419781: push eax
  loc_00419782: mov fs:[00000000h], esp
  loc_00419789: sub esp, 00000088h
  loc_0041978F: push ebx
  loc_00419790: push esi
  loc_00419791: push edi
  loc_00419792: mov var_C, esp
  loc_00419795: mov var_8, 00401608h
  loc_0041979C: xor ebx, ebx
  loc_0041979E: mov var_4, ebx
  loc_004197A1: mov esi, Me
  loc_004197A4: push esi
  loc_004197A5: mov eax, [esi]
  loc_004197A7: call [eax+00000004h]
  loc_004197AA: mov ecx, arg_10
  loc_004197AD: lea eax, var_38
  loc_004197B0: push eax
  loc_004197B1: push esi
  loc_004197B2: mov [ecx], ebx
  loc_004197B4: mov edx, [esi]
  loc_004197B6: mov var_24, ebx
  loc_004197B9: mov var_28, ebx
  loc_004197BC: mov var_2C, ebx
  loc_004197BF: mov var_30, ebx
  loc_004197C2: mov var_34, ebx
  loc_004197C5: mov var_38, ebx
  loc_004197C8: mov var_48, ebx
  loc_004197CB: mov var_58, ebx
  loc_004197CE: mov var_68, ebx
  loc_004197D1: mov var_80, ebx
  loc_004197D4: mov var_84, ebx
  loc_004197DA: mov var_88, ebx
  loc_004197E0: call [edx+00000218h]
  loc_004197E6: cmp eax, ebx
  loc_004197E8: fnclex
  loc_004197EA: jge 004197FEh
  loc_004197EC: push 00000218h
  loc_004197F1: push 0040576Ch
  loc_004197F6: push esi
  loc_004197F7: push eax
  loc_004197F8: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004197FE: mov eax, var_38
  loc_00419801: lea ecx, var_84
  loc_00419807: push eax
  loc_00419808: push ecx
  loc_00419809: mov var_38, ebx
  loc_0041980C: call [00401080h] ; __vbaObjSet
  loc_00419812: push eax
  loc_00419813: lea edx, var_28
  loc_00419816: lea eax, var_88
  loc_0041981C: push edx
  loc_0041981D: push eax
  loc_0041981E: push 00405B4Ch
  loc_00419823: call [00401078h] ; __vbaForEachCollObj
  loc_00419829: mov edi, [00401068h] ; __vbaLateMemSt
  loc_0041982F: cmp eax, ebx
  loc_00419831: jz 004199D6h
  loc_00419837: mov ecx, var_28
  loc_0041983A: push ebx
  loc_0041983B: push 00405C34h ; "Tag"
  loc_00419840: lea edx, var_48
  loc_00419843: push ecx
  loc_00419844: push edx
  loc_00419845: mov var_60, ebx
  loc_00419848: mov var_68, 00008008h
  loc_0041984F: call [004011C8h] ; __vbaLateMemCallLd
  loc_00419855: add esp, 00000010h
  loc_00419858: push eax
  loc_00419859: lea eax, var_68
  loc_0041985C: push eax
  loc_0041985D: call [00401198h] ; __vbaVarTstNe
  loc_00419863: lea ecx, var_48
  loc_00419866: mov si, ax
  loc_00419869: call [00401020h] ; __vbaFreeVar
  loc_0041986F: cmp si, bx
  loc_00419872: jz 004199BBh
  loc_00419878: push 00402208h
  loc_0041987D: call [00401110h] ; __vbaNew
  loc_00419883: lea ecx, var_2C
  loc_00419886: push eax
  loc_00419887: push ecx
  loc_00419888: call [00401080h] ; __vbaObjSet
  loc_0041988E: mov edx, var_28
  loc_00419891: push ebx
  loc_00419892: push 00405C34h ; "Tag"
  loc_00419897: lea eax, var_48
  loc_0041989A: push edx
  loc_0041989B: push eax
  loc_0041989C: call [004011C8h] ; __vbaLateMemCallLd
  loc_004198A2: add esp, 00000010h
  loc_004198A5: push eax
  loc_004198A6: call [00401030h] ; __vbaStrVarMove
  loc_004198AC: mov edx, eax
  loc_004198AE: lea ecx, var_30
  loc_004198B1: call [004011D0h] ; __vbaStrMove
  loc_004198B7: mov eax, var_2C
  loc_004198BA: lea edx, var_30
  loc_004198BD: push edx
  loc_004198BE: push eax
  loc_004198BF: mov ecx, [eax]
  loc_004198C1: call [ecx+00000038h]
  loc_004198C4: cmp eax, ebx
  loc_004198C6: fnclex
  loc_004198C8: jge 004198DCh
  loc_004198CA: mov ecx, var_2C
  loc_004198CD: push 00000038h
  loc_004198CF: push 00405B8Ch
  loc_004198D4: push ecx
  loc_004198D5: push eax
  loc_004198D6: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004198DC: mov esi, [004011F4h] ; __vbaFreeStr
  loc_004198E2: lea ecx, var_30
  loc_004198E5: call __vbaFreeStr
  loc_004198E7: lea ecx, var_48
  loc_004198EA: call [00401020h] ; __vbaFreeVar
  loc_004198F0: mov edx, 00405C40h ; "View"
  loc_004198F5: lea ecx, var_30
  loc_004198F8: call [00401178h] ; __vbaStrCopy
  loc_004198FE: mov eax, var_2C
  loc_00419901: lea ecx, var_34
  loc_00419904: push ecx
  loc_00419905: lea ecx, var_30
  loc_00419908: mov edx, [eax]
  loc_0041990A: push ecx
  loc_0041990B: push eax
  loc_0041990C: call [edx+0000002Ch]
  loc_0041990F: cmp eax, ebx
  loc_00419911: fnclex
  loc_00419913: jge 00419927h
  loc_00419915: mov edx, var_2C
  loc_00419918: push 0000002Ch
  loc_0041991A: push 00405B8Ch
  loc_0041991F: push edx
  loc_00419920: push eax
  loc_00419921: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00419927: mov edx, var_34
  loc_0041992A: lea ecx, var_80
  loc_0041992D: mov var_34, ebx
  loc_00419930: call [004011D0h] ; __vbaStrMove
  loc_00419936: lea ecx, var_30
  loc_00419939: call __vbaFreeStr
  loc_0041993B: mov eax, var_80
  loc_0041993E: mov esi, [004010DCh] ; __vbaStrCmp
  loc_00419944: push eax
  loc_00419945: push 00405B3Ch ; "Manual"
  loc_0041994A: call __vbaStrCmp
  loc_0041994C: test eax, eax
  loc_0041994E: jnz 0041995Ah
  loc_00419950: mov ecx, IsFull
  loc_00419953: cmp [ecx], bx
  loc_00419956: jz 00419975h
  loc_00419958: jmp 00419978h
  loc_0041995A: mov edx, var_80
  loc_0041995D: push edx
  loc_0041995E: push 00405B2Ch ; "Full"
  loc_00419963: call __vbaStrCmp
  loc_00419965: test eax, eax
  loc_00419967: jnz 00419975h
  loc_00419969: mov eax, IsFull
  loc_0041996C: cmp [eax], bx
  loc_0041996F: jnz 00419975h
  loc_00419971: xor eax, eax
  loc_00419973: jmp 00419978h
  loc_00419975: or eax, FFFFFFFFh
  loc_00419978: sub esp, 00000010h
  loc_0041997B: mov ecx, 0000000Bh
  loc_00419980: mov edx, esp
  loc_00419982: mov var_68, ecx
  loc_00419985: mov var_60, eax
  loc_00419988: push 00405C4Ch ; "Visible"
  loc_0041998D: mov [edx], ecx
  loc_0041998F: mov ecx, var_64
  loc_00419992: mov [edx+00000004h], ecx
  loc_00419995: mov ecx, var_28
  loc_00419998: push ecx
  loc_00419999: mov [edx+00000008h], eax
  loc_0041999C: mov eax, var_5C
  loc_0041999F: mov [edx+0000000Ch], eax
  loc_004199A2: call edi
  loc_004199A4: push 00405B8Ch
  loc_004199A9: push ebx
  loc_004199AA: call [004011D4h] ; __vbaCastObj
  loc_004199B0: lea edx, var_2C
  loc_004199B3: push eax
  loc_004199B4: push edx
  loc_004199B5: call [00401080h] ; __vbaObjSet
  loc_004199BB: lea eax, var_28
  loc_004199BE: lea ecx, var_88
  loc_004199C4: push eax
  loc_004199C5: push ecx
  loc_004199C6: push 00405B4Ch
  loc_004199CB: call [004010C0h] ; __vbaNextEachCollObj
  loc_004199D1: jmp 0041982Fh
  loc_004199D6: push 00419A4Fh
  loc_004199DB: jmp 00419A1Ch
  loc_004199DD: test var_4, 04h
  loc_004199E1: jz 004199ECh
  loc_004199E3: lea ecx, var_24
  loc_004199E6: call [00401020h] ; __vbaFreeVar
  loc_004199EC: lea edx, var_34
  loc_004199EF: lea eax, var_30
  loc_004199F2: push edx
  loc_004199F3: push eax
  loc_004199F4: push 00000002h
  loc_004199F6: call [00401180h] ; __vbaFreeStrList
  loc_004199FC: add esp, 0000000Ch
  loc_004199FF: lea ecx, var_38
  loc_00419A02: call [004011F0h] ; __vbaFreeObj
  loc_00419A08: lea ecx, var_58
  loc_00419A0B: lea edx, var_48
  loc_00419A0E: push ecx
  loc_00419A0F: push edx
  loc_00419A10: push 00000002h
  loc_00419A12: call [00401038h] ; __vbaFreeVarList
  loc_00419A18: add esp, 0000000Ch
  loc_00419A1B: ret
  loc_00419A1C: lea ecx, var_80
  loc_00419A1F: call [004011F4h] ; __vbaFreeStr
  loc_00419A25: lea eax, var_88
  loc_00419A2B: lea ecx, var_84
  loc_00419A31: push eax
  loc_00419A32: push ecx
  loc_00419A33: push 00000002h
  loc_00419A35: call [00401040h] ; __vbaFreeObjList
  loc_00419A3B: mov esi, [004011F0h] ; __vbaFreeObj
  loc_00419A41: add esp, 0000000Ch
  loc_00419A44: lea ecx, var_28
  loc_00419A47: call __vbaFreeObj
  loc_00419A49: lea ecx, var_2C
  loc_00419A4C: call __vbaFreeObj
  loc_00419A4E: ret
  loc_00419A4F: mov eax, Me
  loc_00419A52: push eax
  loc_00419A53: mov edx, [eax]
  loc_00419A55: call [edx+00000008h]
  loc_00419A58: mov eax, arg_10
  loc_00419A5B: mov ecx, var_24
  loc_00419A5E: mov edx, var_20
  loc_00419A61: mov [eax], ecx
  loc_00419A63: mov ecx, var_1C
  loc_00419A66: mov [eax+00000004h], edx
  loc_00419A69: mov edx, var_18
  loc_00419A6C: mov [eax+00000008h], ecx
  loc_00419A6F: mov [eax+0000000Ch], edx
  loc_00419A72: mov eax, var_4
  loc_00419A75: mov ecx, var_14
  loc_00419A78: pop edi
  loc_00419A79: pop esi
  loc_00419A7A: mov fs:[00000000h], ecx
  loc_00419A81: pop ebx
  loc_00419A82: mov esp, ebp
  loc_00419A84: pop ebp
  loc_00419A85: retn 000Ch
End Function

Public Function WriteLampElectricalTestHeaderRecords(TestSerial, WaferID, RecipeName, Voltage, Delay1, Delay2, Delay3, Averages, MeterDelay, Iterations, NPLC) '41A740
  loc_0041A740: push ebp
  loc_0041A741: mov ebp, esp
  loc_0041A743: sub esp, 0000000Ch
  loc_0041A746: push 00401AA6h ; __vbaExceptHandler
  loc_0041A74B: mov eax, fs:[00000000h]
  loc_0041A751: push eax
  loc_0041A752: mov fs:[00000000h], esp
  loc_0041A759: sub esp, 00000090h
  loc_0041A75F: push ebx
  loc_0041A760: push esi
  loc_0041A761: push edi
  loc_0041A762: mov var_C, esp
  loc_0041A765: mov var_8, 00401650h
  loc_0041A76C: xor edi, edi
  loc_0041A76E: mov var_4, edi
  loc_0041A771: mov eax, Me
  loc_0041A774: push eax
  loc_0041A775: mov ecx, [eax]
  loc_0041A777: call [ecx+00000004h]
  loc_0041A77A: mov edx, arg_38
  loc_0041A77D: mov eax, TestSerial
  loc_0041A780: mov ebx, 00000008h
  loc_0041A785: mov var_78, edi
  loc_0041A788: mov [edx], edi
  loc_0041A78A: mov ecx, [eax]
  loc_0041A78C: push ecx
  loc_0041A78D: mov var_28, edi
  loc_0041A790: mov var_2C, edi
  loc_0041A793: mov var_30, edi
  loc_0041A796: mov var_34, edi
  loc_0041A799: mov var_38, edi
  loc_0041A79C: mov var_48, edi
  loc_0041A79F: mov var_58, edi
  loc_0041A7A2: mov var_68, edi
  loc_0041A7A5: mov var_70, 0040775Ch ; "SELECT * FROM tblLampElectricalTest WHERE tblLampElectricalTest.fldTestSerial = "
  loc_0041A7AC: mov var_78, ebx
  loc_0041A7AF: call [00401018h] ; __vbaStrI4
  loc_0041A7B5: mov var_40, eax
  loc_0041A7B8: lea edx, var_48
  loc_0041A7BB: lea eax, var_58
  loc_0041A7BE: push edx
  loc_0041A7BF: push eax
  loc_0041A7C0: mov var_48, ebx
  loc_0041A7C3: call [004010A4h] ; rtcTrimVar
  loc_0041A7C9: lea ecx, var_78
  loc_0041A7CC: lea edx, var_58
  loc_0041A7CF: push ecx
  loc_0041A7D0: lea eax, var_68
  loc_0041A7D3: push edx
  loc_0041A7D4: push eax
  loc_0041A7D5: call [004011ACh] ; __vbaVarAdd
  loc_0041A7DB: push eax
  loc_0041A7DC: call [00401030h] ; __vbaStrVarMove
  loc_0041A7E2: mov edx, eax
  loc_0041A7E4: lea ecx, var_2C
  loc_0041A7E7: call [004011D0h] ; __vbaStrMove
  loc_0041A7ED: lea ecx, var_68
  loc_0041A7F0: lea edx, var_58
  loc_0041A7F3: push ecx
  loc_0041A7F4: lea eax, var_48
  loc_0041A7F7: push edx
  loc_0041A7F8: push eax
  loc_0041A7F9: push 00000003h
  loc_0041A7FB: call [00401038h] ; __vbaFreeVarList
  loc_0041A801: add esp, 00000010h
  loc_0041A804: push 0040714Ch
  loc_0041A809: call [00401110h] ; __vbaNew
  loc_0041A80F: lea ecx, var_30
  loc_0041A812: push eax
  loc_0041A813: push ecx
  loc_0041A814: call [00401080h] ; __vbaObjSet
  loc_0041A81A: mov eax, var_30
  loc_0041A81D: push 00000003h
  loc_0041A81F: push eax
  loc_0041A820: mov edx, [eax]
  loc_0041A822: call [edx+000000F0h]
  loc_0041A828: cmp eax, edi
  loc_0041A82A: fnclex
  loc_0041A82C: jge 0041A847h
  loc_0041A82E: mov ecx, var_30
  loc_0041A831: mov esi, [0040105Ch] ; __vbaHresultCheckObj
  loc_0041A837: push 000000F0h
  loc_0041A83C: push 004072E8h
  loc_0041A841: push ecx
  loc_0041A842: push eax
  loc_0041A843: call __vbaHresultCheckObj
  loc_0041A845: jmp 0041A84Dh
  loc_0041A847: mov esi, [0040105Ch] ; __vbaHresultCheckObj
  loc_0041A84D: mov eax, var_30
  loc_0041A850: push 00000001h
  loc_0041A852: push eax
  loc_0041A853: mov edx, [eax]
  loc_0041A855: call [edx+0000004Ch]
  loc_0041A858: cmp eax, edi
  loc_0041A85A: fnclex
  loc_0041A85C: jge 0041A86Ch
  loc_0041A85E: mov ecx, var_30
  loc_0041A861: push 0000004Ch
  loc_0041A863: push 004072E8h
  loc_0041A868: push ecx
  loc_0041A869: push eax
  loc_0041A86A: call __vbaHresultCheckObj
  loc_0041A86C: mov eax, var_30
  loc_0041A86F: push 00000003h
  loc_0041A871: push eax
  loc_0041A872: mov edx, [eax]
  loc_0041A874: call [edx+0000005Ch]
  loc_0041A877: cmp eax, edi
  loc_0041A879: fnclex
  loc_0041A87B: jge 0041A88Bh
  loc_0041A87D: mov ecx, var_30
  loc_0041A880: push 0000005Ch
  loc_0041A882: push 004072E8h
  loc_0041A887: push ecx
  loc_0041A888: push eax
  loc_0041A889: call __vbaHresultCheckObj
  loc_0041A88B: push FFFFFFFFh
  loc_0041A88D: push FFFFFFFFh
  loc_0041A88F: push FFFFFFFFh
  loc_0041A891: mov eax, [00423028h]
  loc_0041A896: sub esp, 00000010h
  loc_0041A899: mov var_78, ebx
  loc_0041A89C: mov ebx, esp
  loc_0041A89E: mov ecx, 00000009h
  loc_0041A8A3: sub esp, 00000010h
  loc_0041A8A6: mov edx, var_2C
  loc_0041A8A9: mov [ebx], ecx
  loc_0041A8AB: mov ecx, var_84
  loc_0041A8B1: mov edi, var_30
  loc_0041A8B4: mov var_70, edx
  loc_0041A8B7: mov [ebx+00000004h], ecx
  loc_0041A8BA: mov ecx, esp
  loc_0041A8BC: mov edi, [edi]
  loc_0041A8BE: mov [ebx+00000008h], eax
  loc_0041A8C1: mov eax, var_7C
  loc_0041A8C4: mov [ebx+0000000Ch], eax
  loc_0041A8C7: mov eax, var_78
  loc_0041A8CA: mov [ecx], eax
  loc_0041A8CC: mov eax, var_74
  loc_0041A8CF: mov [ecx+00000004h], eax
  loc_0041A8D2: mov eax, var_30
  loc_0041A8D5: push eax
  loc_0041A8D6: mov [ecx+00000008h], edx
  loc_0041A8D9: mov edx, var_6C
  loc_0041A8DC: mov [ecx+0000000Ch], edx
  loc_0041A8DF: call [edi+000000A0h]
  loc_0041A8E5: test eax, eax
  loc_0041A8E7: fnclex
  loc_0041A8E9: jge 0041A8FCh
  loc_0041A8EB: mov ecx, var_30
  loc_0041A8EE: push 000000A0h
  loc_0041A8F3: push 004072E8h
  loc_0041A8F8: push ecx
  loc_0041A8F9: push eax
  loc_0041A8FA: call __vbaHresultCheckObj
  loc_0041A8FC: sub esp, 00000010h
  loc_0041A8FF: mov ecx, 0000000Ah
  loc_0041A904: mov ebx, esp
  loc_0041A906: mov var_78, ecx
  loc_0041A909: mov eax, 80020004h
  loc_0041A90E: sub esp, 00000010h
  loc_0041A911: mov [ebx], ecx
  loc_0041A913: mov ecx, var_84
  loc_0041A919: mov edx, eax
  loc_0041A91B: mov edi, var_30
  loc_0041A91E: mov [ebx+00000004h], ecx
  loc_0041A921: mov ecx, esp
  loc_0041A923: mov var_70, edx
  loc_0041A926: mov edi, [edi]
  loc_0041A928: mov [ebx+00000008h], eax
  loc_0041A92B: mov eax, var_7C
  loc_0041A92E: mov [ebx+0000000Ch], eax
  loc_0041A931: mov eax, var_78
  loc_0041A934: mov [ecx], eax
  loc_0041A936: mov eax, var_74
  loc_0041A939: mov [ecx+00000004h], eax
  loc_0041A93C: mov eax, var_30
  loc_0041A93F: push eax
  loc_0041A940: mov [ecx+00000008h], edx
  loc_0041A943: mov edx, var_6C
  loc_0041A946: mov [ecx+0000000Ch], edx
  loc_0041A949: call [edi+00000078h]
  loc_0041A94C: test eax, eax
  loc_0041A94E: fnclex
  loc_0041A950: jge 0041A960h
  loc_0041A952: mov ecx, var_30
  loc_0041A955: push 00000078h
  loc_0041A957: push 004072E8h
  loc_0041A95C: push ecx
  loc_0041A95D: push eax
  loc_0041A95E: call __vbaHresultCheckObj
  loc_0041A960: mov eax, var_30
  loc_0041A963: lea ecx, var_34
  loc_0041A966: push ecx
  loc_0041A967: push eax
  loc_0041A968: mov edx, [eax]
  loc_0041A96A: call [edx+00000054h]
  loc_0041A96D: test eax, eax
  loc_0041A96F: fnclex
  loc_0041A971: jge 0041A981h
  loc_0041A973: mov edx, var_30
  loc_0041A976: push 00000054h
  loc_0041A978: push 004072E8h
  loc_0041A97D: push edx
  loc_0041A97E: push eax
  loc_0041A97F: call __vbaHresultCheckObj
  loc_0041A981: lea ebx, var_38
  loc_0041A984: mov eax, var_34
  loc_0041A987: push ebx
  loc_0041A988: mov edx, 00000008h
  loc_0041A98D: sub esp, 00000010h
  loc_0041A990: mov var_78, edx
  loc_0041A993: mov ebx, esp
  loc_0041A995: mov ecx, 00407804h ; "fldTestSerial"
  loc_0041A99A: mov var_70, ecx
  loc_0041A99D: mov edi, [eax]
  loc_0041A99F: mov [ebx], edx
  loc_0041A9A1: mov edx, var_74
  loc_0041A9A4: push eax
  loc_0041A9A5: mov var_90, eax
  loc_0041A9AB: mov [ebx+00000004h], edx
  loc_0041A9AE: mov [ebx+00000008h], ecx
  loc_0041A9B1: mov ecx, var_6C
  loc_0041A9B4: mov [ebx+0000000Ch], ecx
  loc_0041A9B7: call [edi+00000028h]
  loc_0041A9BA: test eax, eax
  loc_0041A9BC: fnclex
  loc_0041A9BE: jge 0041A9D1h
  loc_0041A9C0: mov edx, var_90
  loc_0041A9C6: push 00000028h
  loc_0041A9C8: push 00407390h
  loc_0041A9CD: push edx
  loc_0041A9CE: push eax
  loc_0041A9CF: call __vbaHresultCheckObj
  loc_0041A9D1: mov ecx, TestSerial
  loc_0041A9D4: sub esp, 00000010h
  loc_0041A9D7: mov eax, var_38
  loc_0041A9DA: mov ebx, esp
  loc_0041A9DC: mov ecx, [ecx]
  loc_0041A9DE: mov edx, 00000003h
  loc_0041A9E3: mov edi, [eax]
  loc_0041A9E5: mov [ebx], edx
  loc_0041A9E7: mov edx, var_84
  loc_0041A9ED: push eax
  loc_0041A9EE: mov [ebx+00000004h], edx
  loc_0041A9F1: mov var_98, eax
  loc_0041A9F7: mov [ebx+00000008h], ecx
  loc_0041A9FA: mov ecx, var_7C
  loc_0041A9FD: mov [ebx+0000000Ch], ecx
  loc_0041AA00: call [edi+00000038h]
  loc_0041AA03: test eax, eax
  loc_0041AA05: fnclex
  loc_0041AA07: jge 0041AA1Ah
  loc_0041AA09: mov edx, var_98
  loc_0041AA0F: push 00000038h
  loc_0041AA11: push 004073A0h
  loc_0041AA16: push edx
  loc_0041AA17: push eax
  loc_0041AA18: call __vbaHresultCheckObj
  loc_0041AA1A: lea eax, var_38
  loc_0041AA1D: lea ecx, var_34
  loc_0041AA20: push eax
  loc_0041AA21: push ecx
  loc_0041AA22: push 00000002h
  loc_0041AA24: call [00401040h] ; __vbaFreeObjList
  loc_0041AA2A: mov eax, var_30
  loc_0041AA2D: add esp, 0000000Ch
  loc_0041AA30: lea ecx, var_34
  loc_0041AA33: mov edx, [eax]
  loc_0041AA35: push ecx
  loc_0041AA36: push eax
  loc_0041AA37: call [edx+00000054h]
  loc_0041AA3A: test eax, eax
  loc_0041AA3C: fnclex
  loc_0041AA3E: jge 0041AA4Eh
  loc_0041AA40: mov edx, var_30
  loc_0041AA43: push 00000054h
  loc_0041AA45: push 004072E8h
  loc_0041AA4A: push edx
  loc_0041AA4B: push eax
  loc_0041AA4C: call __vbaHresultCheckObj
  loc_0041AA4E: lea ebx, var_38
  loc_0041AA51: mov eax, var_34
  loc_0041AA54: push ebx
  loc_0041AA55: mov edx, 00000008h
  loc_0041AA5A: sub esp, 00000010h
  loc_0041AA5D: mov edi, [eax]
  loc_0041AA5F: mov ebx, esp
  loc_0041AA61: mov ecx, 00407824h ; "fldProberName"
  loc_0041AA66: push eax
  loc_0041AA67: mov var_90, eax
  loc_0041AA6D: mov [ebx], edx
  loc_0041AA6F: mov edx, var_84
  loc_0041AA75: mov [ebx+00000004h], edx
  loc_0041AA78: mov [ebx+00000008h], ecx
  loc_0041AA7B: mov ecx, var_7C
  loc_0041AA7E: mov [ebx+0000000Ch], ecx
  loc_0041AA81: call [edi+00000028h]
  loc_0041AA84: test eax, eax
  loc_0041AA86: fnclex
  loc_0041AA88: jge 0041AA9Bh
  loc_0041AA8A: mov edx, var_90
  loc_0041AA90: push 00000028h
  loc_0041AA92: push 00407390h
  loc_0041AA97: push edx
  loc_0041AA98: push eax
  loc_0041AA99: call __vbaHresultCheckObj
  loc_0041AA9B: sub esp, 00000010h
  loc_0041AA9E: mov ecx, 00000008h
  loc_0041AAA3: mov edx, esp
  loc_0041AAA5: mov var_78, ecx
  loc_0041AAA8: mov edi, var_38
  loc_0041AAAB: mov eax, 00405CA4h ; "IMTPRB02"
  loc_0041AAB0: mov [edx], ecx
  loc_0041AAB2: mov ecx, var_74
  loc_0041AAB5: mov var_70, eax
  loc_0041AAB8: push 00405C88h ; "ProberName"
  loc_0041AABD: mov [edx+00000004h], ecx
  loc_0041AAC0: push 00405C78h ; "Names"
  loc_0041AAC5: push 00405C60h ; "IMTProber"
  loc_0041AACA: mov [edx+00000008h], eax
  loc_0041AACD: mov eax, var_6C
  loc_0041AAD0: mov [edx+0000000Ch], eax
  loc_0041AAD3: call [004011A0h] ; rtcGetSetting
  loc_0041AAD9: sub esp, 00000010h
  loc_0041AADC: mov ecx, 00000008h
  loc_0041AAE1: mov ebx, esp
  loc_0041AAE3: mov var_48, ecx
  loc_0041AAE6: mov var_40, eax
  loc_0041AAE9: mov edx, [edi]
  loc_0041AAEB: mov [ebx], ecx
  loc_0041AAED: mov ecx, var_44
  loc_0041AAF0: push edi
  loc_0041AAF1: mov [ebx+00000004h], ecx
  loc_0041AAF4: mov [ebx+00000008h], eax
  loc_0041AAF7: mov eax, var_3C
  loc_0041AAFA: mov [ebx+0000000Ch], eax
  loc_0041AAFD: call [edx+00000038h]
  loc_0041AB00: test eax, eax
  loc_0041AB02: fnclex
  loc_0041AB04: jge 0041AB11h
  loc_0041AB06: push 00000038h
  loc_0041AB08: push 004073A0h
  loc_0041AB0D: push edi
  loc_0041AB0E: push eax
  loc_0041AB0F: call __vbaHresultCheckObj
  loc_0041AB11: lea ecx, var_38
  loc_0041AB14: lea edx, var_34
  loc_0041AB17: push ecx
  loc_0041AB18: push edx
  loc_0041AB19: push 00000002h
  loc_0041AB1B: call [00401040h] ; __vbaFreeObjList
  loc_0041AB21: add esp, 0000000Ch
  loc_0041AB24: lea ecx, var_48
  loc_0041AB27: call [00401020h] ; __vbaFreeVar
  loc_0041AB2D: mov eax, var_30
  loc_0041AB30: lea edx, var_34
  loc_0041AB33: push edx
  loc_0041AB34: push eax
  loc_0041AB35: mov ecx, [eax]
  loc_0041AB37: call [ecx+00000054h]
  loc_0041AB3A: test eax, eax
  loc_0041AB3C: fnclex
  loc_0041AB3E: jge 0041AB4Eh
  loc_0041AB40: mov ecx, var_30
  loc_0041AB43: push 00000054h
  loc_0041AB45: push 004072E8h
  loc_0041AB4A: push ecx
  loc_0041AB4B: push eax
  loc_0041AB4C: call __vbaHresultCheckObj
  loc_0041AB4E: lea ebx, var_38
  loc_0041AB51: mov eax, var_34
  loc_0041AB54: push ebx
  loc_0041AB55: mov edx, 00000008h
  loc_0041AB5A: sub esp, 00000010h
  loc_0041AB5D: mov var_78, edx
  loc_0041AB60: mov ebx, esp
  loc_0041AB62: mov ecx, 00407844h ; "fldRecipeName"
  loc_0041AB67: mov var_70, ecx
  loc_0041AB6A: mov edi, [eax]
  loc_0041AB6C: mov [ebx], edx
  loc_0041AB6E: mov edx, var_74
  loc_0041AB71: push eax
  loc_0041AB72: mov var_90, eax
  loc_0041AB78: mov [ebx+00000004h], edx
  loc_0041AB7B: mov [ebx+00000008h], ecx
  loc_0041AB7E: mov ecx, var_6C
  loc_0041AB81: mov [ebx+0000000Ch], ecx
  loc_0041AB84: call [edi+00000028h]
  loc_0041AB87: test eax, eax
  loc_0041AB89: fnclex
  loc_0041AB8B: jge 0041AB9Eh
  loc_0041AB8D: mov edx, var_90
  loc_0041AB93: push 00000028h
  loc_0041AB95: push 00407390h
  loc_0041AB9A: push edx
  loc_0041AB9B: push eax
  loc_0041AB9C: call __vbaHresultCheckObj
  loc_0041AB9E: mov ecx, RecipeName
  loc_0041ABA1: sub esp, 00000010h
  loc_0041ABA4: mov eax, var_38
  loc_0041ABA7: mov ebx, esp
  loc_0041ABA9: mov ecx, [ecx]
  loc_0041ABAB: mov edx, 00000008h
  loc_0041ABB0: mov edi, [eax]
  loc_0041ABB2: mov [ebx], edx
  loc_0041ABB4: mov edx, var_84
  loc_0041ABBA: push eax
  loc_0041ABBB: mov [ebx+00000004h], edx
  loc_0041ABBE: mov var_98, eax
  loc_0041ABC4: mov [ebx+00000008h], ecx
  loc_0041ABC7: mov ecx, var_7C
  loc_0041ABCA: mov [ebx+0000000Ch], ecx
  loc_0041ABCD: call [edi+00000038h]
  loc_0041ABD0: test eax, eax
  loc_0041ABD2: fnclex
  loc_0041ABD4: jge 0041ABE7h
  loc_0041ABD6: mov edx, var_98
  loc_0041ABDC: push 00000038h
  loc_0041ABDE: push 004073A0h
  loc_0041ABE3: push edx
  loc_0041ABE4: push eax
  loc_0041ABE5: call __vbaHresultCheckObj
  loc_0041ABE7: lea eax, var_38
  loc_0041ABEA: lea ecx, var_34
  loc_0041ABED: push eax
  loc_0041ABEE: push ecx
  loc_0041ABEF: push 00000002h
  loc_0041ABF1: call [00401040h] ; __vbaFreeObjList
  loc_0041ABF7: mov eax, var_30
  loc_0041ABFA: add esp, 0000000Ch
  loc_0041ABFD: lea ecx, var_34
  loc_0041AC00: mov edx, [eax]
  loc_0041AC02: push ecx
  loc_0041AC03: push eax
  loc_0041AC04: call [edx+00000054h]
  loc_0041AC07: test eax, eax
  loc_0041AC09: fnclex
  loc_0041AC0B: jge 0041AC1Bh
  loc_0041AC0D: mov edx, var_30
  loc_0041AC10: push 00000054h
  loc_0041AC12: push 004072E8h
  loc_0041AC17: push edx
  loc_0041AC18: push eax
  loc_0041AC19: call __vbaHresultCheckObj
  loc_0041AC1B: lea ebx, var_38
  loc_0041AC1E: mov eax, var_34
  loc_0041AC21: push ebx
  loc_0041AC22: mov edx, 00000008h
  loc_0041AC27: sub esp, 00000010h
  loc_0041AC2A: mov var_78, edx
  loc_0041AC2D: mov ebx, esp
  loc_0041AC2F: mov ecx, 00407864h ; "fldStartDate"
  loc_0041AC34: mov var_70, ecx
  loc_0041AC37: mov edi, [eax]
  loc_0041AC39: mov [ebx], edx
  loc_0041AC3B: mov edx, var_74
  loc_0041AC3E: push eax
  loc_0041AC3F: mov var_90, eax
  loc_0041AC45: mov [ebx+00000004h], edx
  loc_0041AC48: mov [ebx+00000008h], ecx
  loc_0041AC4B: mov ecx, var_6C
  loc_0041AC4E: mov [ebx+0000000Ch], ecx
  loc_0041AC51: call [edi+00000028h]
  loc_0041AC54: test eax, eax
  loc_0041AC56: fnclex
  loc_0041AC58: jge 0041AC6Bh
  loc_0041AC5A: mov edx, var_90
  loc_0041AC60: push 00000028h
  loc_0041AC62: push 00407390h
  loc_0041AC67: push edx
  loc_0041AC68: push eax
  loc_0041AC69: call __vbaHresultCheckObj
  loc_0041AC6B: mov edi, var_38
  loc_0041AC6E: lea eax, var_48
  loc_0041AC71: push eax
  loc_0041AC72: call [004011E4h] ; rtcGetPresentDate
  loc_0041AC78: mov eax, var_48
  loc_0041AC7B: sub esp, 00000010h
  loc_0041AC7E: mov edx, esp
  loc_0041AC80: mov ecx, [edi]
  loc_0041AC82: push edi
  loc_0041AC83: mov [edx], eax
  loc_0041AC85: mov eax, var_44
  loc_0041AC88: mov [edx+00000004h], eax
  loc_0041AC8B: mov eax, var_40
  loc_0041AC8E: mov [edx+00000008h], eax
  loc_0041AC91: mov eax, var_3C
  loc_0041AC94: mov [edx+0000000Ch], eax
  loc_0041AC97: call [ecx+00000038h]
  loc_0041AC9A: test eax, eax
  loc_0041AC9C: fnclex
  loc_0041AC9E: jge 0041ACABh
  loc_0041ACA0: push 00000038h
  loc_0041ACA2: push 004073A0h
  loc_0041ACA7: push edi
  loc_0041ACA8: push eax
  loc_0041ACA9: call __vbaHresultCheckObj
  loc_0041ACAB: lea ecx, var_38
  loc_0041ACAE: lea edx, var_34
  loc_0041ACB1: push ecx
  loc_0041ACB2: push edx
  loc_0041ACB3: push 00000002h
  loc_0041ACB5: call [00401040h] ; __vbaFreeObjList
  loc_0041ACBB: add esp, 0000000Ch
  loc_0041ACBE: lea ecx, var_48
  loc_0041ACC1: call [00401020h] ; __vbaFreeVar
  loc_0041ACC7: mov eax, var_30
  loc_0041ACCA: lea edx, var_34
  loc_0041ACCD: push edx
  loc_0041ACCE: push eax
  loc_0041ACCF: mov ecx, [eax]
  loc_0041ACD1: call [ecx+00000054h]
  loc_0041ACD4: test eax, eax
  loc_0041ACD6: fnclex
  loc_0041ACD8: jge 0041ACE8h
  loc_0041ACDA: mov ecx, var_30
  loc_0041ACDD: push 00000054h
  loc_0041ACDF: push 004072E8h
  loc_0041ACE4: push ecx
  loc_0041ACE5: push eax
  loc_0041ACE6: call __vbaHresultCheckObj
  loc_0041ACE8: lea ebx, var_38
  loc_0041ACEB: mov eax, var_34
  loc_0041ACEE: push ebx
  loc_0041ACEF: mov edx, 00000008h
  loc_0041ACF4: sub esp, 00000010h
  loc_0041ACF7: mov var_78, edx
  loc_0041ACFA: mov ebx, esp
  loc_0041ACFC: mov ecx, 00407884h ; "fldOperator"
  loc_0041AD01: mov var_70, ecx
  loc_0041AD04: mov edi, [eax]
  loc_0041AD06: mov [ebx], edx
  loc_0041AD08: mov edx, var_74
  loc_0041AD0B: push eax
  loc_0041AD0C: mov var_90, eax
  loc_0041AD12: mov [ebx+00000004h], edx
  loc_0041AD15: mov [ebx+00000008h], ecx
  loc_0041AD18: mov ecx, var_6C
  loc_0041AD1B: mov [ebx+0000000Ch], ecx
  loc_0041AD1E: call [edi+00000028h]
  loc_0041AD21: test eax, eax
  loc_0041AD23: fnclex
  loc_0041AD25: jge 0041AD38h
  loc_0041AD27: mov edx, var_90
  loc_0041AD2D: push 00000028h
  loc_0041AD2F: push 00407390h
  loc_0041AD34: push edx
  loc_0041AD35: push eax
  loc_0041AD36: call __vbaHresultCheckObj
  loc_0041AD38: mov eax, [00423010h]
  loc_0041AD3D: mov edi, var_38
  loc_0041AD40: test eax, eax
  loc_0041AD42: jnz 0041AD59h
  loc_0041AD44: push 00423010h
  loc_0041AD49: push 004025D8h
  loc_0041AD4E: call [00401168h] ; __vbaNew2
  loc_0041AD54: mov eax, [00423010h]
  loc_0041AD59: mov ecx, [eax]
  loc_0041AD5B: push eax
  loc_0041AD5C: call [ecx+00000310h]
  loc_0041AD62: sub esp, 00000010h
  loc_0041AD65: mov ecx, 00000009h
  loc_0041AD6A: mov ebx, esp
  loc_0041AD6C: mov var_48, ecx
  loc_0041AD6F: mov var_40, eax
  loc_0041AD72: mov edx, [edi]
  loc_0041AD74: mov [ebx], ecx
  loc_0041AD76: mov ecx, var_44
  loc_0041AD79: push edi
  loc_0041AD7A: mov [ebx+00000004h], ecx
  loc_0041AD7D: mov [ebx+00000008h], eax
  loc_0041AD80: mov eax, var_3C
  loc_0041AD83: mov [ebx+0000000Ch], eax
  loc_0041AD86: call [edx+00000038h]
  loc_0041AD89: test eax, eax
  loc_0041AD8B: fnclex
  loc_0041AD8D: jge 0041AD9Ah
  loc_0041AD8F: push 00000038h
  loc_0041AD91: push 004073A0h
  loc_0041AD96: push edi
  loc_0041AD97: push eax
  loc_0041AD98: call __vbaHresultCheckObj
  loc_0041AD9A: lea ecx, var_38
  loc_0041AD9D: lea edx, var_34
  loc_0041ADA0: push ecx
  loc_0041ADA1: push edx
  loc_0041ADA2: push 00000002h
  loc_0041ADA4: call [00401040h] ; __vbaFreeObjList
  loc_0041ADAA: add esp, 0000000Ch
  loc_0041ADAD: lea ecx, var_48
  loc_0041ADB0: call [00401020h] ; __vbaFreeVar
  loc_0041ADB6: mov eax, var_30
  loc_0041ADB9: lea edx, var_34
  loc_0041ADBC: push edx
  loc_0041ADBD: push eax
  loc_0041ADBE: mov ecx, [eax]
  loc_0041ADC0: call [ecx+00000054h]
  loc_0041ADC3: test eax, eax
  loc_0041ADC5: fnclex
  loc_0041ADC7: jge 0041ADD7h
  loc_0041ADC9: mov ecx, var_30
  loc_0041ADCC: push 00000054h
  loc_0041ADCE: push 004072E8h
  loc_0041ADD3: push ecx
  loc_0041ADD4: push eax
  loc_0041ADD5: call __vbaHresultCheckObj
  loc_0041ADD7: lea ebx, var_38
  loc_0041ADDA: mov eax, var_34
  loc_0041ADDD: push ebx
  loc_0041ADDE: mov edx, 00000008h
  loc_0041ADE3: sub esp, 00000010h
  loc_0041ADE6: mov var_78, edx
  loc_0041ADE9: mov ebx, esp
  loc_0041ADEB: mov ecx, 004078A0h ; "fldWaferID"
  loc_0041ADF0: mov var_70, ecx
  loc_0041ADF3: mov edi, [eax]
  loc_0041ADF5: mov [ebx], edx
  loc_0041ADF7: mov edx, var_74
  loc_0041ADFA: push eax
  loc_0041ADFB: mov var_90, eax
  loc_0041AE01: mov [ebx+00000004h], edx
  loc_0041AE04: mov [ebx+00000008h], ecx
  loc_0041AE07: mov ecx, var_6C
  loc_0041AE0A: mov [ebx+0000000Ch], ecx
  loc_0041AE0D: call [edi+00000028h]
  loc_0041AE10: test eax, eax
  loc_0041AE12: fnclex
  loc_0041AE14: jge 0041AE27h
  loc_0041AE16: mov edx, var_90
  loc_0041AE1C: push 00000028h
  loc_0041AE1E: push 00407390h
  loc_0041AE23: push edx
  loc_0041AE24: push eax
  loc_0041AE25: call __vbaHresultCheckObj
  loc_0041AE27: mov ecx, WaferID
  loc_0041AE2A: sub esp, 00000010h
  loc_0041AE2D: mov eax, var_38
  loc_0041AE30: mov ebx, esp
  loc_0041AE32: mov ecx, [ecx]
  loc_0041AE34: mov edx, 00000008h
  loc_0041AE39: mov edi, [eax]
  loc_0041AE3B: mov [ebx], edx
  loc_0041AE3D: mov edx, var_84
  loc_0041AE43: push eax
  loc_0041AE44: mov [ebx+00000004h], edx
  loc_0041AE47: mov var_98, eax
  loc_0041AE4D: mov [ebx+00000008h], ecx
  loc_0041AE50: mov ecx, var_7C
  loc_0041AE53: mov [ebx+0000000Ch], ecx
  loc_0041AE56: call [edi+00000038h]
  loc_0041AE59: test eax, eax
  loc_0041AE5B: fnclex
  loc_0041AE5D: jge 0041AE70h
  loc_0041AE5F: mov edx, var_98
  loc_0041AE65: push 00000038h
  loc_0041AE67: push 004073A0h
  loc_0041AE6C: push edx
  loc_0041AE6D: push eax
  loc_0041AE6E: call __vbaHresultCheckObj
  loc_0041AE70: lea eax, var_38
  loc_0041AE73: lea ecx, var_34
  loc_0041AE76: push eax
  loc_0041AE77: push ecx
  loc_0041AE78: push 00000002h
  loc_0041AE7A: call [00401040h] ; __vbaFreeObjList
  loc_0041AE80: mov eax, var_30
  loc_0041AE83: add esp, 0000000Ch
  loc_0041AE86: lea ecx, var_34
  loc_0041AE89: mov edx, [eax]
  loc_0041AE8B: push ecx
  loc_0041AE8C: push eax
  loc_0041AE8D: call [edx+00000054h]
  loc_0041AE90: test eax, eax
  loc_0041AE92: fnclex
  loc_0041AE94: jge 0041AEA4h
  loc_0041AE96: mov edx, var_30
  loc_0041AE99: push 00000054h
  loc_0041AE9B: push 004072E8h
  loc_0041AEA0: push edx
  loc_0041AEA1: push eax
  loc_0041AEA2: call __vbaHresultCheckObj
  loc_0041AEA4: lea ebx, var_38
  loc_0041AEA7: mov eax, var_34
  loc_0041AEAA: push ebx
  loc_0041AEAB: mov edx, 00000008h
  loc_0041AEB0: sub esp, 00000010h
  loc_0041AEB3: mov var_78, edx
  loc_0041AEB6: mov ebx, esp
  loc_0041AEB8: mov ecx, 004078BCh ; "fldProcessStep"
  loc_0041AEBD: mov var_70, ecx
  loc_0041AEC0: mov edi, [eax]
  loc_0041AEC2: mov [ebx], edx
  loc_0041AEC4: mov edx, var_74
  loc_0041AEC7: push eax
  loc_0041AEC8: mov var_90, eax
  loc_0041AECE: mov [ebx+00000004h], edx
  loc_0041AED1: mov [ebx+00000008h], ecx
  loc_0041AED4: mov ecx, var_6C
  loc_0041AED7: mov [ebx+0000000Ch], ecx
  loc_0041AEDA: call [edi+00000028h]
  loc_0041AEDD: test eax, eax
  loc_0041AEDF: fnclex
  loc_0041AEE1: jge 0041AEF4h
  loc_0041AEE3: mov edx, var_90
  loc_0041AEE9: push 00000028h
  loc_0041AEEB: push 00407390h
  loc_0041AEF0: push edx
  loc_0041AEF1: push eax
  loc_0041AEF2: call __vbaHresultCheckObj
  loc_0041AEF4: mov eax, [00423010h]
  loc_0041AEF9: mov edi, var_38
  loc_0041AEFC: test eax, eax
  loc_0041AEFE: jnz 0041AF15h
  loc_0041AF00: push 00423010h
  loc_0041AF05: push 004025D8h
  loc_0041AF0A: call [00401168h] ; __vbaNew2
  loc_0041AF10: mov eax, [00423010h]
  loc_0041AF15: mov ecx, [eax]
  loc_0041AF17: push eax
  loc_0041AF18: call [ecx+0000030Ch]
  loc_0041AF1E: sub esp, 00000010h
  loc_0041AF21: mov ecx, 00000009h
  loc_0041AF26: mov ebx, esp
  loc_0041AF28: mov var_48, ecx
  loc_0041AF2B: mov var_40, eax
  loc_0041AF2E: mov edx, [edi]
  loc_0041AF30: mov [ebx], ecx
  loc_0041AF32: mov ecx, var_44
  loc_0041AF35: push edi
  loc_0041AF36: mov [ebx+00000004h], ecx
  loc_0041AF39: mov [ebx+00000008h], eax
  loc_0041AF3C: mov eax, var_3C
  loc_0041AF3F: mov [ebx+0000000Ch], eax
  loc_0041AF42: call [edx+00000038h]
  loc_0041AF45: test eax, eax
  loc_0041AF47: fnclex
  loc_0041AF49: jge 0041AF56h
  loc_0041AF4B: push 00000038h
  loc_0041AF4D: push 004073A0h
  loc_0041AF52: push edi
  loc_0041AF53: push eax
  loc_0041AF54: call __vbaHresultCheckObj
  loc_0041AF56: lea ecx, var_38
  loc_0041AF59: lea edx, var_34
  loc_0041AF5C: push ecx
  loc_0041AF5D: push edx
  loc_0041AF5E: push 00000002h
  loc_0041AF60: call [00401040h] ; __vbaFreeObjList
  loc_0041AF66: add esp, 0000000Ch
  loc_0041AF69: lea ecx, var_48
  loc_0041AF6C: call [00401020h] ; __vbaFreeVar
  loc_0041AF72: sub esp, 00000010h
  loc_0041AF75: mov ecx, 0000000Ah
  loc_0041AF7A: mov ebx, esp
  loc_0041AF7C: mov var_78, ecx
  loc_0041AF7F: mov eax, 80020004h
  loc_0041AF84: sub esp, 00000010h
  loc_0041AF87: mov [ebx], ecx
  loc_0041AF89: mov ecx, var_84
  loc_0041AF8F: mov edx, eax
  loc_0041AF91: mov edi, var_30
  loc_0041AF94: mov [ebx+00000004h], ecx
  loc_0041AF97: mov ecx, esp
  loc_0041AF99: mov var_70, edx
  loc_0041AF9C: mov edi, [edi]
  loc_0041AF9E: mov [ebx+00000008h], eax
  loc_0041AFA1: mov eax, var_7C
  loc_0041AFA4: mov [ebx+0000000Ch], eax
  loc_0041AFA7: mov eax, var_78
  loc_0041AFAA: mov [ecx], eax
  loc_0041AFAC: mov eax, var_74
  loc_0041AFAF: mov [ecx+00000004h], eax
  loc_0041AFB2: mov eax, var_30
  loc_0041AFB5: push eax
  loc_0041AFB6: mov [ecx+00000008h], edx
  loc_0041AFB9: mov edx, var_6C
  loc_0041AFBC: mov [ecx+0000000Ch], edx
  loc_0041AFBF: call [edi+000000ACh]
  loc_0041AFC5: test eax, eax
  loc_0041AFC7: fnclex
  loc_0041AFC9: jge 0041AFDCh
  loc_0041AFCB: mov ecx, var_30
  loc_0041AFCE: push 000000ACh
  loc_0041AFD3: push 004072E8h
  loc_0041AFD8: push ecx
  loc_0041AFD9: push eax
  loc_0041AFDA: call __vbaHresultCheckObj
  loc_0041AFDC: mov eax, var_30
  loc_0041AFDF: push eax
  loc_0041AFE0: mov edx, [eax]
  loc_0041AFE2: call [edx+00000080h]
  loc_0041AFE8: test eax, eax
  loc_0041AFEA: fnclex
  loc_0041AFEC: jge 0041AFFFh
  loc_0041AFEE: mov ecx, var_30
  loc_0041AFF1: push 00000080h
  loc_0041AFF6: push 004072E8h
  loc_0041AFFB: push ecx
  loc_0041AFFC: push eax
  loc_0041AFFD: call __vbaHresultCheckObj
  loc_0041AFFF: push 0040713Ch
  loc_0041B004: push 00000000h
  loc_0041B006: call [004011D4h] ; __vbaCastObj
  loc_0041B00C: mov edi, [00401080h] ; __vbaObjSet
  loc_0041B012: lea edx, var_30
  loc_0041B015: push eax
  loc_0041B016: push edx
  loc_0041B017: call edi
  loc_0041B019: call [004010A0h] ; rtcDoEvents
  loc_0041B01F: mov eax, TestSerial
  loc_0041B022: mov ebx, 00000008h
  loc_0041B027: mov var_70, 0040792Ch ; "SELECT * FROM tblLampElectricalTestRegime WHERE tblLampElectricalTestRegime.fldTestSerial = "
  loc_0041B02E: mov var_78, ebx
  loc_0041B031: mov ecx, [eax]
  loc_0041B033: push ecx
  loc_0041B034: call [00401018h] ; __vbaStrI4
  loc_0041B03A: mov var_40, eax
  loc_0041B03D: lea edx, var_48
  loc_0041B040: lea eax, var_58
  loc_0041B043: push edx
  loc_0041B044: push eax
  loc_0041B045: mov var_48, ebx
  loc_0041B048: call [004010A4h] ; rtcTrimVar
  loc_0041B04E: lea ecx, var_78
  loc_0041B051: lea edx, var_58
  loc_0041B054: push ecx
  loc_0041B055: lea eax, var_68
  loc_0041B058: push edx
  loc_0041B059: push eax
  loc_0041B05A: call [004011ACh] ; __vbaVarAdd
  loc_0041B060: push eax
  loc_0041B061: call [00401030h] ; __vbaStrVarMove
  loc_0041B067: mov edx, eax
  loc_0041B069: lea ecx, var_2C
  loc_0041B06C: call [004011D0h] ; __vbaStrMove
  loc_0041B072: lea ecx, var_68
  loc_0041B075: lea edx, var_58
  loc_0041B078: push ecx
  loc_0041B079: lea eax, var_48
  loc_0041B07C: push edx
  loc_0041B07D: push eax
  loc_0041B07E: push 00000003h
  loc_0041B080: call [00401038h] ; __vbaFreeVarList
  loc_0041B086: add esp, 00000010h
  loc_0041B089: push 0040714Ch
  loc_0041B08E: call [00401110h] ; __vbaNew
  loc_0041B094: lea ecx, var_30
  loc_0041B097: push eax
  loc_0041B098: push ecx
  loc_0041B099: call edi
  loc_0041B09B: mov eax, var_30
  loc_0041B09E: push 00000003h
  loc_0041B0A0: push eax
  loc_0041B0A1: mov edx, [eax]
  loc_0041B0A3: call [edx+000000F0h]
  loc_0041B0A9: test eax, eax
  loc_0041B0AB: fnclex
  loc_0041B0AD: jge 0041B0C0h
  loc_0041B0AF: mov ecx, var_30
  loc_0041B0B2: push 000000F0h
  loc_0041B0B7: push 004072E8h
  loc_0041B0BC: push ecx
  loc_0041B0BD: push eax
  loc_0041B0BE: call __vbaHresultCheckObj
  loc_0041B0C0: mov eax, var_30
  loc_0041B0C3: push 00000001h
  loc_0041B0C5: push eax
  loc_0041B0C6: mov edx, [eax]
  loc_0041B0C8: call [edx+0000004Ch]
  loc_0041B0CB: test eax, eax
  loc_0041B0CD: fnclex
  loc_0041B0CF: jge 0041B0DFh
  loc_0041B0D1: mov ecx, var_30
  loc_0041B0D4: push 0000004Ch
  loc_0041B0D6: push 004072E8h
  loc_0041B0DB: push ecx
  loc_0041B0DC: push eax
  loc_0041B0DD: call __vbaHresultCheckObj
  loc_0041B0DF: mov eax, var_30
  loc_0041B0E2: push 00000003h
  loc_0041B0E4: push eax
  loc_0041B0E5: mov edx, [eax]
  loc_0041B0E7: call [edx+0000005Ch]
  loc_0041B0EA: test eax, eax
  loc_0041B0EC: fnclex
  loc_0041B0EE: jge 0041B0FEh
  loc_0041B0F0: mov ecx, var_30
  loc_0041B0F3: push 0000005Ch
  loc_0041B0F5: push 004072E8h
  loc_0041B0FA: push ecx
  loc_0041B0FB: push eax
  loc_0041B0FC: call __vbaHresultCheckObj
  loc_0041B0FE: push FFFFFFFFh
  loc_0041B100: push FFFFFFFFh
  loc_0041B102: push FFFFFFFFh
  loc_0041B104: mov eax, [00423028h]
  loc_0041B109: sub esp, 00000010h
  loc_0041B10C: mov var_78, ebx
  loc_0041B10F: mov ebx, esp
  loc_0041B111: mov ecx, 00000009h
  loc_0041B116: sub esp, 00000010h
  loc_0041B119: mov edx, var_2C
  loc_0041B11C: mov [ebx], ecx
  loc_0041B11E: mov ecx, var_84
  loc_0041B124: mov edi, var_30
  loc_0041B127: mov var_70, edx
  loc_0041B12A: mov [ebx+00000004h], ecx
  loc_0041B12D: mov ecx, esp
  loc_0041B12F: mov edi, [edi]
  loc_0041B131: mov [ebx+00000008h], eax
  loc_0041B134: mov eax, var_7C
  loc_0041B137: mov [ebx+0000000Ch], eax
  loc_0041B13A: mov eax, var_78
  loc_0041B13D: mov [ecx], eax
  loc_0041B13F: mov eax, var_74
  loc_0041B142: mov [ecx+00000004h], eax
  loc_0041B145: mov eax, var_30
  loc_0041B148: push eax
  loc_0041B149: mov [ecx+00000008h], edx
  loc_0041B14C: mov edx, var_6C
  loc_0041B14F: mov [ecx+0000000Ch], edx
  loc_0041B152: call [edi+000000A0h]
  loc_0041B158: test eax, eax
  loc_0041B15A: fnclex
  loc_0041B15C: jge 0041B16Fh
  loc_0041B15E: mov ecx, var_30
  loc_0041B161: push 000000A0h
  loc_0041B166: push 004072E8h
  loc_0041B16B: push ecx
  loc_0041B16C: push eax
  loc_0041B16D: call __vbaHresultCheckObj
  loc_0041B16F: sub esp, 00000010h
  loc_0041B172: mov ecx, 0000000Ah
  loc_0041B177: mov ebx, esp
  loc_0041B179: mov var_78, ecx
  loc_0041B17C: mov eax, 80020004h
  loc_0041B181: sub esp, 00000010h
  loc_0041B184: mov [ebx], ecx
  loc_0041B186: mov ecx, var_84
  loc_0041B18C: mov edx, eax
  loc_0041B18E: mov edi, var_30
  loc_0041B191: mov [ebx+00000004h], ecx
  loc_0041B194: mov ecx, esp
  loc_0041B196: mov var_70, edx
  loc_0041B199: mov edi, [edi]
  loc_0041B19B: mov [ebx+00000008h], eax
  loc_0041B19E: mov eax, var_7C
  loc_0041B1A1: mov [ebx+0000000Ch], eax
  loc_0041B1A4: mov eax, var_78
  loc_0041B1A7: mov [ecx], eax
  loc_0041B1A9: mov eax, var_74
  loc_0041B1AC: mov [ecx+00000004h], eax
  loc_0041B1AF: mov eax, var_30
  loc_0041B1B2: push eax
  loc_0041B1B3: mov [ecx+00000008h], edx
  loc_0041B1B6: mov edx, var_6C
  loc_0041B1B9: mov [ecx+0000000Ch], edx
  loc_0041B1BC: call [edi+00000078h]
  loc_0041B1BF: test eax, eax
  loc_0041B1C1: fnclex
  loc_0041B1C3: jge 0041B1D3h
  loc_0041B1C5: mov ecx, var_30
  loc_0041B1C8: push 00000078h
  loc_0041B1CA: push 004072E8h
  loc_0041B1CF: push ecx
  loc_0041B1D0: push eax
  loc_0041B1D1: call __vbaHresultCheckObj
  loc_0041B1D3: mov eax, var_30
  loc_0041B1D6: lea ecx, var_34
  loc_0041B1D9: push ecx
  loc_0041B1DA: push eax
  loc_0041B1DB: mov edx, [eax]
  loc_0041B1DD: call [edx+00000054h]
  loc_0041B1E0: test eax, eax
  loc_0041B1E2: fnclex
  loc_0041B1E4: jge 0041B1F4h
  loc_0041B1E6: mov edx, var_30
  loc_0041B1E9: push 00000054h
  loc_0041B1EB: push 004072E8h
  loc_0041B1F0: push edx
  loc_0041B1F1: push eax
  loc_0041B1F2: call __vbaHresultCheckObj
  loc_0041B1F4: lea ebx, var_38
  loc_0041B1F7: mov eax, var_34
  loc_0041B1FA: push ebx
  loc_0041B1FB: mov edx, 00000008h
  loc_0041B200: sub esp, 00000010h
  loc_0041B203: mov var_78, edx
  loc_0041B206: mov ebx, esp
  loc_0041B208: mov ecx, 00407804h ; "fldTestSerial"
  loc_0041B20D: mov var_70, ecx
  loc_0041B210: mov edi, [eax]
  loc_0041B212: mov [ebx], edx
  loc_0041B214: mov edx, var_74
  loc_0041B217: push eax
  loc_0041B218: mov var_90, eax
  loc_0041B21E: mov [ebx+00000004h], edx
  loc_0041B221: mov [ebx+00000008h], ecx
  loc_0041B224: mov ecx, var_6C
  loc_0041B227: mov [ebx+0000000Ch], ecx
  loc_0041B22A: call [edi+00000028h]
  loc_0041B22D: test eax, eax
  loc_0041B22F: fnclex
  loc_0041B231: jge 0041B244h
  loc_0041B233: mov edx, var_90
  loc_0041B239: push 00000028h
  loc_0041B23B: push 00407390h
  loc_0041B240: push edx
  loc_0041B241: push eax
  loc_0041B242: call __vbaHresultCheckObj
  loc_0041B244: mov ecx, TestSerial
  loc_0041B247: sub esp, 00000010h
  loc_0041B24A: mov eax, var_38
  loc_0041B24D: mov ebx, esp
  loc_0041B24F: mov ecx, [ecx]
  loc_0041B251: mov edx, 00000003h
  loc_0041B256: mov edi, [eax]
  loc_0041B258: mov [ebx], edx
  loc_0041B25A: mov edx, var_84
  loc_0041B260: push eax
  loc_0041B261: mov [ebx+00000004h], edx
  loc_0041B264: mov var_98, eax
  loc_0041B26A: mov [ebx+00000008h], ecx
  loc_0041B26D: mov ecx, var_7C
  loc_0041B270: mov [ebx+0000000Ch], ecx
  loc_0041B273: call [edi+00000038h]
  loc_0041B276: test eax, eax
  loc_0041B278: fnclex
  loc_0041B27A: jge 0041B28Dh
  loc_0041B27C: mov edx, var_98
  loc_0041B282: push 00000038h
  loc_0041B284: push 004073A0h
  loc_0041B289: push edx
  loc_0041B28A: push eax
  loc_0041B28B: call __vbaHresultCheckObj
  loc_0041B28D: lea eax, var_38
  loc_0041B290: lea ecx, var_34
  loc_0041B293: push eax
  loc_0041B294: push ecx
  loc_0041B295: push 00000002h
  loc_0041B297: call [00401040h] ; __vbaFreeObjList
  loc_0041B29D: mov eax, var_30
  loc_0041B2A0: add esp, 0000000Ch
  loc_0041B2A3: lea ecx, var_34
  loc_0041B2A6: mov edx, [eax]
  loc_0041B2A8: push ecx
  loc_0041B2A9: push eax
  loc_0041B2AA: call [edx+00000054h]
  loc_0041B2AD: test eax, eax
  loc_0041B2AF: fnclex
  loc_0041B2B1: jge 0041B2C1h
  loc_0041B2B3: mov edx, var_30
  loc_0041B2B6: push 00000054h
  loc_0041B2B8: push 004072E8h
  loc_0041B2BD: push edx
  loc_0041B2BE: push eax
  loc_0041B2BF: call __vbaHresultCheckObj
  loc_0041B2C1: lea ebx, var_38
  loc_0041B2C4: mov eax, var_34
  loc_0041B2C7: push ebx
  loc_0041B2C8: mov edx, 00000008h
  loc_0041B2CD: sub esp, 00000010h
  loc_0041B2D0: mov var_78, edx
  loc_0041B2D3: mov ebx, esp
  loc_0041B2D5: mov ecx, 004079ECh ; "fldVoltage"
  loc_0041B2DA: mov var_70, ecx
  loc_0041B2DD: mov edi, [eax]
  loc_0041B2DF: mov [ebx], edx
  loc_0041B2E1: mov edx, var_74
  loc_0041B2E4: push eax
  loc_0041B2E5: mov var_90, eax
  loc_0041B2EB: mov [ebx+00000004h], edx
  loc_0041B2EE: mov [ebx+00000008h], ecx
  loc_0041B2F1: mov ecx, var_6C
  loc_0041B2F4: mov [ebx+0000000Ch], ecx
  loc_0041B2F7: call [edi+00000028h]
  loc_0041B2FA: test eax, eax
  loc_0041B2FC: fnclex
  loc_0041B2FE: jge 0041B311h
  loc_0041B300: mov edx, var_90
  loc_0041B306: push 00000028h
  loc_0041B308: push 00407390h
  loc_0041B30D: push edx
  loc_0041B30E: push eax
  loc_0041B30F: call __vbaHresultCheckObj
  loc_0041B311: mov ecx, Voltage
  loc_0041B314: sub esp, 00000010h
  loc_0041B317: mov eax, var_38
  loc_0041B31A: mov ebx, esp
  loc_0041B31C: mov edx, [ecx]
  loc_0041B31E: mov ecx, [ecx+00000004h]
  loc_0041B321: mov var_7C, ecx
  loc_0041B324: mov ecx, 00000005h
  loc_0041B329: mov edi, [eax]
  loc_0041B32B: mov [ebx], ecx
  loc_0041B32D: mov ecx, var_84
  loc_0041B333: push eax
  loc_0041B334: mov [ebx+00000004h], ecx
  loc_0041B337: mov var_98, eax
  loc_0041B33D: mov [ebx+00000008h], edx
  loc_0041B340: mov edx, var_7C
  loc_0041B343: mov [ebx+0000000Ch], edx
  loc_0041B346: call [edi+00000038h]
  loc_0041B349: test eax, eax
  loc_0041B34B: fnclex
  loc_0041B34D: jge 0041B360h
  loc_0041B34F: mov ecx, var_98
  loc_0041B355: push 00000038h
  loc_0041B357: push 004073A0h
  loc_0041B35C: push ecx
  loc_0041B35D: push eax
  loc_0041B35E: call __vbaHresultCheckObj
  loc_0041B360: lea edx, var_38
  loc_0041B363: lea eax, var_34
  loc_0041B366: push edx
  loc_0041B367: push eax
  loc_0041B368: push 00000002h
  loc_0041B36A: call [00401040h] ; __vbaFreeObjList
  loc_0041B370: mov eax, var_30
  loc_0041B373: add esp, 0000000Ch
  loc_0041B376: lea edx, var_34
  loc_0041B379: mov ecx, [eax]
  loc_0041B37B: push edx
  loc_0041B37C: push eax
  loc_0041B37D: call [ecx+00000054h]
  loc_0041B380: test eax, eax
  loc_0041B382: fnclex
  loc_0041B384: jge 0041B394h
  loc_0041B386: mov ecx, var_30
  loc_0041B389: push 00000054h
  loc_0041B38B: push 004072E8h
  loc_0041B390: push ecx
  loc_0041B391: push eax
  loc_0041B392: call __vbaHresultCheckObj
  loc_0041B394: lea ebx, var_38
  loc_0041B397: mov eax, var_34
  loc_0041B39A: push ebx
  loc_0041B39B: mov edx, 00000008h
  loc_0041B3A0: sub esp, 00000010h
  loc_0041B3A3: mov var_78, edx
  loc_0041B3A6: mov ebx, esp
  loc_0041B3A8: mov ecx, 00407A08h ; "fldDelay1"
  loc_0041B3AD: mov var_70, ecx
  loc_0041B3B0: mov edi, [eax]
  loc_0041B3B2: mov [ebx], edx
  loc_0041B3B4: mov edx, var_74
  loc_0041B3B7: push eax
  loc_0041B3B8: mov var_90, eax
  loc_0041B3BE: mov [ebx+00000004h], edx
  loc_0041B3C1: mov [ebx+00000008h], ecx
  loc_0041B3C4: mov ecx, var_6C
  loc_0041B3C7: mov [ebx+0000000Ch], ecx
  loc_0041B3CA: call [edi+00000028h]
  loc_0041B3CD: test eax, eax
  loc_0041B3CF: fnclex
  loc_0041B3D1: jge 0041B3E4h
  loc_0041B3D3: mov edx, var_90
  loc_0041B3D9: push 00000028h
  loc_0041B3DB: push 00407390h
  loc_0041B3E0: push edx
  loc_0041B3E1: push eax
  loc_0041B3E2: call __vbaHresultCheckObj
  loc_0041B3E4: mov ecx, Delay1
  loc_0041B3E7: sub esp, 00000010h
  loc_0041B3EA: mov eax, var_38
  loc_0041B3ED: mov ebx, esp
  loc_0041B3EF: mov ecx, [ecx]
  loc_0041B3F1: mov edx, 00000003h
  loc_0041B3F6: mov edi, [eax]
  loc_0041B3F8: mov [ebx], edx
  loc_0041B3FA: mov edx, var_84
  loc_0041B400: push eax
  loc_0041B401: mov [ebx+00000004h], edx
  loc_0041B404: mov var_98, eax
  loc_0041B40A: mov [ebx+00000008h], ecx
  loc_0041B40D: mov ecx, var_7C
  loc_0041B410: mov [ebx+0000000Ch], ecx
  loc_0041B413: call [edi+00000038h]
  loc_0041B416: test eax, eax
  loc_0041B418: fnclex
  loc_0041B41A: jge 0041B42Dh
  loc_0041B41C: mov edx, var_98
  loc_0041B422: push 00000038h
  loc_0041B424: push 004073A0h
  loc_0041B429: push edx
  loc_0041B42A: push eax
  loc_0041B42B: call __vbaHresultCheckObj
  loc_0041B42D: lea eax, var_38
  loc_0041B430: lea ecx, var_34
  loc_0041B433: push eax
  loc_0041B434: push ecx
  loc_0041B435: push 00000002h
  loc_0041B437: call [00401040h] ; __vbaFreeObjList
  loc_0041B43D: mov eax, var_30
  loc_0041B440: add esp, 0000000Ch
  loc_0041B443: lea ecx, var_34
  loc_0041B446: mov edx, [eax]
  loc_0041B448: push ecx
  loc_0041B449: push eax
  loc_0041B44A: call [edx+00000054h]
  loc_0041B44D: test eax, eax
  loc_0041B44F: fnclex
  loc_0041B451: jge 0041B461h
  loc_0041B453: mov edx, var_30
  loc_0041B456: push 00000054h
  loc_0041B458: push 004072E8h
  loc_0041B45D: push edx
  loc_0041B45E: push eax
  loc_0041B45F: call __vbaHresultCheckObj
  loc_0041B461: lea ebx, var_38
  loc_0041B464: mov eax, var_34
  loc_0041B467: push ebx
  loc_0041B468: mov edx, 00000008h
  loc_0041B46D: sub esp, 00000010h
  loc_0041B470: mov var_78, edx
  loc_0041B473: mov ebx, esp
  loc_0041B475: mov ecx, 00407A20h ; "fldDelay2"
  loc_0041B47A: mov var_70, ecx
  loc_0041B47D: mov edi, [eax]
  loc_0041B47F: mov [ebx], edx
  loc_0041B481: mov edx, var_74
  loc_0041B484: push eax
  loc_0041B485: mov var_90, eax
  loc_0041B48B: mov [ebx+00000004h], edx
  loc_0041B48E: mov [ebx+00000008h], ecx
  loc_0041B491: mov ecx, var_6C
  loc_0041B494: mov [ebx+0000000Ch], ecx
  loc_0041B497: call [edi+00000028h]
  loc_0041B49A: test eax, eax
  loc_0041B49C: fnclex
  loc_0041B49E: jge 0041B4B1h
  loc_0041B4A0: mov edx, var_90
  loc_0041B4A6: push 00000028h
  loc_0041B4A8: push 00407390h
  loc_0041B4AD: push edx
  loc_0041B4AE: push eax
  loc_0041B4AF: call __vbaHresultCheckObj
  loc_0041B4B1: mov ecx, Delay2
  loc_0041B4B4: sub esp, 00000010h
  loc_0041B4B7: mov eax, var_38
  loc_0041B4BA: mov ebx, esp
  loc_0041B4BC: mov ecx, [ecx]
  loc_0041B4BE: mov edx, 00000003h
  loc_0041B4C3: mov edi, [eax]
  loc_0041B4C5: mov [ebx], edx
  loc_0041B4C7: mov edx, var_84
  loc_0041B4CD: push eax
  loc_0041B4CE: mov [ebx+00000004h], edx
  loc_0041B4D1: mov var_98, eax
  loc_0041B4D7: mov [ebx+00000008h], ecx
  loc_0041B4DA: mov ecx, var_7C
  loc_0041B4DD: mov [ebx+0000000Ch], ecx
  loc_0041B4E0: call [edi+00000038h]
  loc_0041B4E3: test eax, eax
  loc_0041B4E5: fnclex
  loc_0041B4E7: jge 0041B4FAh
  loc_0041B4E9: mov edx, var_98
  loc_0041B4EF: push 00000038h
  loc_0041B4F1: push 004073A0h
  loc_0041B4F6: push edx
  loc_0041B4F7: push eax
  loc_0041B4F8: call __vbaHresultCheckObj
  loc_0041B4FA: lea eax, var_38
  loc_0041B4FD: lea ecx, var_34
  loc_0041B500: push eax
  loc_0041B501: push ecx
  loc_0041B502: push 00000002h
  loc_0041B504: call [00401040h] ; __vbaFreeObjList
  loc_0041B50A: mov eax, var_30
  loc_0041B50D: add esp, 0000000Ch
  loc_0041B510: lea ecx, var_34
  loc_0041B513: mov edx, [eax]
  loc_0041B515: push ecx
  loc_0041B516: push eax
  loc_0041B517: call [edx+00000054h]
  loc_0041B51A: test eax, eax
  loc_0041B51C: fnclex
  loc_0041B51E: jge 0041B52Eh
  loc_0041B520: mov edx, var_30
  loc_0041B523: push 00000054h
  loc_0041B525: push 004072E8h
  loc_0041B52A: push edx
  loc_0041B52B: push eax
  loc_0041B52C: call __vbaHresultCheckObj
  loc_0041B52E: lea ebx, var_38
  loc_0041B531: mov eax, var_34
  loc_0041B534: push ebx
  loc_0041B535: mov edx, 00000008h
  loc_0041B53A: sub esp, 00000010h
  loc_0041B53D: mov var_78, edx
  loc_0041B540: mov ebx, esp
  loc_0041B542: mov ecx, 00407A38h ; "fldDelay3"
  loc_0041B547: mov var_70, ecx
  loc_0041B54A: mov edi, [eax]
  loc_0041B54C: mov [ebx], edx
  loc_0041B54E: mov edx, var_74
  loc_0041B551: push eax
  loc_0041B552: mov var_90, eax
  loc_0041B558: mov [ebx+00000004h], edx
  loc_0041B55B: mov [ebx+00000008h], ecx
  loc_0041B55E: mov ecx, var_6C
  loc_0041B561: mov [ebx+0000000Ch], ecx
  loc_0041B564: call [edi+00000028h]
  loc_0041B567: test eax, eax
  loc_0041B569: fnclex
  loc_0041B56B: jge 0041B57Eh
  loc_0041B56D: mov edx, var_90
  loc_0041B573: push 00000028h
  loc_0041B575: push 00407390h
  loc_0041B57A: push edx
  loc_0041B57B: push eax
  loc_0041B57C: call __vbaHresultCheckObj
  loc_0041B57E: mov ecx, Delay3
  loc_0041B581: sub esp, 00000010h
  loc_0041B584: mov eax, var_38
  loc_0041B587: mov ebx, esp
  loc_0041B589: mov ecx, [ecx]
  loc_0041B58B: mov edx, 00000003h
  loc_0041B590: mov edi, [eax]
  loc_0041B592: mov [ebx], edx
  loc_0041B594: mov edx, var_84
  loc_0041B59A: push eax
  loc_0041B59B: mov [ebx+00000004h], edx
  loc_0041B59E: mov var_98, eax
  loc_0041B5A4: mov [ebx+00000008h], ecx
  loc_0041B5A7: mov ecx, var_7C
  loc_0041B5AA: mov [ebx+0000000Ch], ecx
  loc_0041B5AD: call [edi+00000038h]
  loc_0041B5B0: test eax, eax
  loc_0041B5B2: fnclex
  loc_0041B5B4: jge 0041B5C7h
  loc_0041B5B6: mov edx, var_98
  loc_0041B5BC: push 00000038h
  loc_0041B5BE: push 004073A0h
  loc_0041B5C3: push edx
  loc_0041B5C4: push eax
  loc_0041B5C5: call __vbaHresultCheckObj
  loc_0041B5C7: lea eax, var_38
  loc_0041B5CA: lea ecx, var_34
  loc_0041B5CD: push eax
  loc_0041B5CE: push ecx
  loc_0041B5CF: push 00000002h
  loc_0041B5D1: call [00401040h] ; __vbaFreeObjList
  loc_0041B5D7: mov eax, var_30
  loc_0041B5DA: add esp, 0000000Ch
  loc_0041B5DD: lea ecx, var_34
  loc_0041B5E0: mov edx, [eax]
  loc_0041B5E2: push ecx
  loc_0041B5E3: push eax
  loc_0041B5E4: call [edx+00000054h]
  loc_0041B5E7: test eax, eax
  loc_0041B5E9: fnclex
  loc_0041B5EB: jge 0041B5FBh
  loc_0041B5ED: mov edx, var_30
  loc_0041B5F0: push 00000054h
  loc_0041B5F2: push 004072E8h
  loc_0041B5F7: push edx
  loc_0041B5F8: push eax
  loc_0041B5F9: call __vbaHresultCheckObj
  loc_0041B5FB: lea ebx, var_38
  loc_0041B5FE: mov eax, var_34
  loc_0041B601: push ebx
  loc_0041B602: mov edx, 00000008h
  loc_0041B607: sub esp, 00000010h
  loc_0041B60A: mov var_78, edx
  loc_0041B60D: mov ebx, esp
  loc_0041B60F: mov ecx, 00407A50h ; "fldAverages"
  loc_0041B614: mov var_70, ecx
  loc_0041B617: mov edi, [eax]
  loc_0041B619: mov [ebx], edx
  loc_0041B61B: mov edx, var_74
  loc_0041B61E: push eax
  loc_0041B61F: mov var_90, eax
  loc_0041B625: mov [ebx+00000004h], edx
  loc_0041B628: mov [ebx+00000008h], ecx
  loc_0041B62B: mov ecx, var_6C
  loc_0041B62E: mov [ebx+0000000Ch], ecx
  loc_0041B631: call [edi+00000028h]
  loc_0041B634: test eax, eax
  loc_0041B636: fnclex
  loc_0041B638: jge 0041B64Bh
  loc_0041B63A: mov edx, var_90
  loc_0041B640: push 00000028h
  loc_0041B642: push 00407390h
  loc_0041B647: push edx
  loc_0041B648: push eax
  loc_0041B649: call __vbaHresultCheckObj
  loc_0041B64B: mov ecx, Averages
  loc_0041B64E: sub esp, 00000010h
  loc_0041B651: mov eax, var_38
  loc_0041B654: mov ebx, esp
  loc_0041B656: mov ecx, [ecx]
  loc_0041B658: mov edx, 00000003h
  loc_0041B65D: mov edi, [eax]
  loc_0041B65F: mov [ebx], edx
  loc_0041B661: mov edx, var_84
  loc_0041B667: push eax
  loc_0041B668: mov [ebx+00000004h], edx
  loc_0041B66B: mov var_98, eax
  loc_0041B671: mov [ebx+00000008h], ecx
  loc_0041B674: mov ecx, var_7C
  loc_0041B677: mov [ebx+0000000Ch], ecx
  loc_0041B67A: call [edi+00000038h]
  loc_0041B67D: test eax, eax
  loc_0041B67F: fnclex
  loc_0041B681: jge 0041B694h
  loc_0041B683: mov edx, var_98
  loc_0041B689: push 00000038h
  loc_0041B68B: push 004073A0h
  loc_0041B690: push edx
  loc_0041B691: push eax
  loc_0041B692: call __vbaHresultCheckObj
  loc_0041B694: lea eax, var_38
  loc_0041B697: lea ecx, var_34
  loc_0041B69A: push eax
  loc_0041B69B: push ecx
  loc_0041B69C: push 00000002h
  loc_0041B69E: call [00401040h] ; __vbaFreeObjList
  loc_0041B6A4: mov eax, var_30
  loc_0041B6A7: add esp, 0000000Ch
  loc_0041B6AA: lea ecx, var_34
  loc_0041B6AD: mov edx, [eax]
  loc_0041B6AF: push ecx
  loc_0041B6B0: push eax
  loc_0041B6B1: call [edx+00000054h]
  loc_0041B6B4: test eax, eax
  loc_0041B6B6: fnclex
  loc_0041B6B8: jge 0041B6C8h
  loc_0041B6BA: mov edx, var_30
  loc_0041B6BD: push 00000054h
  loc_0041B6BF: push 004072E8h
  loc_0041B6C4: push edx
  loc_0041B6C5: push eax
  loc_0041B6C6: call __vbaHresultCheckObj
  loc_0041B6C8: lea ebx, var_38
  loc_0041B6CB: mov eax, var_34
  loc_0041B6CE: push ebx
  loc_0041B6CF: mov edx, 00000008h
  loc_0041B6D4: sub esp, 00000010h
  loc_0041B6D7: mov var_78, edx
  loc_0041B6DA: mov ebx, esp
  loc_0041B6DC: mov ecx, 00407A6Ch ; "fldMeterDelay"
  loc_0041B6E1: mov var_70, ecx
  loc_0041B6E4: mov edi, [eax]
  loc_0041B6E6: mov [ebx], edx
  loc_0041B6E8: mov edx, var_74
  loc_0041B6EB: push eax
  loc_0041B6EC: mov var_90, eax
  loc_0041B6F2: mov [ebx+00000004h], edx
  loc_0041B6F5: mov [ebx+00000008h], ecx
  loc_0041B6F8: mov ecx, var_6C
  loc_0041B6FB: mov [ebx+0000000Ch], ecx
  loc_0041B6FE: call [edi+00000028h]
  loc_0041B701: test eax, eax
  loc_0041B703: fnclex
  loc_0041B705: jge 0041B718h
  loc_0041B707: mov edx, var_90
  loc_0041B70D: push 00000028h
  loc_0041B70F: push 00407390h
  loc_0041B714: push edx
  loc_0041B715: push eax
  loc_0041B716: call __vbaHresultCheckObj
  loc_0041B718: mov ecx, MeterDelay
  loc_0041B71B: sub esp, 00000010h
  loc_0041B71E: mov eax, var_38
  loc_0041B721: mov ebx, esp
  loc_0041B723: mov edx, [ecx]
  loc_0041B725: mov ecx, [ecx+00000004h]
  loc_0041B728: mov var_7C, ecx
  loc_0041B72B: mov ecx, 00000005h
  loc_0041B730: mov edi, [eax]
  loc_0041B732: mov [ebx], ecx
  loc_0041B734: mov ecx, var_84
  loc_0041B73A: push eax
  loc_0041B73B: mov [ebx+00000004h], ecx
  loc_0041B73E: mov var_98, eax
  loc_0041B744: mov [ebx+00000008h], edx
  loc_0041B747: mov edx, var_7C
  loc_0041B74A: mov [ebx+0000000Ch], edx
  loc_0041B74D: call [edi+00000038h]
  loc_0041B750: test eax, eax
  loc_0041B752: fnclex
  loc_0041B754: jge 0041B767h
  loc_0041B756: mov ecx, var_98
  loc_0041B75C: push 00000038h
  loc_0041B75E: push 004073A0h
  loc_0041B763: push ecx
  loc_0041B764: push eax
  loc_0041B765: call __vbaHresultCheckObj
  loc_0041B767: lea edx, var_38
  loc_0041B76A: lea eax, var_34
  loc_0041B76D: push edx
  loc_0041B76E: push eax
  loc_0041B76F: push 00000002h
  loc_0041B771: call [00401040h] ; __vbaFreeObjList
  loc_0041B777: mov eax, var_30
  loc_0041B77A: add esp, 0000000Ch
  loc_0041B77D: lea edx, var_34
  loc_0041B780: mov ecx, [eax]
  loc_0041B782: push edx
  loc_0041B783: push eax
  loc_0041B784: call [ecx+00000054h]
  loc_0041B787: test eax, eax
  loc_0041B789: fnclex
  loc_0041B78B: jge 0041B79Bh
  loc_0041B78D: mov ecx, var_30
  loc_0041B790: push 00000054h
  loc_0041B792: push 004072E8h
  loc_0041B797: push ecx
  loc_0041B798: push eax
  loc_0041B799: call __vbaHresultCheckObj
  loc_0041B79B: lea ebx, var_38
  loc_0041B79E: mov eax, var_34
  loc_0041B7A1: push ebx
  loc_0041B7A2: mov edx, 00000008h
  loc_0041B7A7: sub esp, 00000010h
  loc_0041B7AA: mov var_78, edx
  loc_0041B7AD: mov ebx, esp
  loc_0041B7AF: mov ecx, 00407A8Ch ; "fldIterations"
  loc_0041B7B4: mov var_70, ecx
  loc_0041B7B7: mov edi, [eax]
  loc_0041B7B9: mov [ebx], edx
  loc_0041B7BB: mov edx, var_74
  loc_0041B7BE: push eax
  loc_0041B7BF: mov var_90, eax
  loc_0041B7C5: mov [ebx+00000004h], edx
  loc_0041B7C8: mov [ebx+00000008h], ecx
  loc_0041B7CB: mov ecx, var_6C
  loc_0041B7CE: mov [ebx+0000000Ch], ecx
  loc_0041B7D1: call [edi+00000028h]
  loc_0041B7D4: test eax, eax
  loc_0041B7D6: fnclex
  loc_0041B7D8: jge 0041B7EBh
  loc_0041B7DA: mov edx, var_90
  loc_0041B7E0: push 00000028h
  loc_0041B7E2: push 00407390h
  loc_0041B7E7: push edx
  loc_0041B7E8: push eax
  loc_0041B7E9: call __vbaHresultCheckObj
  loc_0041B7EB: mov ecx, Iterations
  loc_0041B7EE: sub esp, 00000010h
  loc_0041B7F1: mov eax, var_38
  loc_0041B7F4: mov ebx, esp
  loc_0041B7F6: mov ecx, [ecx]
  loc_0041B7F8: mov edx, 00000003h
  loc_0041B7FD: mov edi, [eax]
  loc_0041B7FF: mov [ebx], edx
  loc_0041B801: mov edx, var_84
  loc_0041B807: push eax
  loc_0041B808: mov [ebx+00000004h], edx
  loc_0041B80B: mov var_98, eax
  loc_0041B811: mov [ebx+00000008h], ecx
  loc_0041B814: mov ecx, var_7C
  loc_0041B817: mov [ebx+0000000Ch], ecx
  loc_0041B81A: call [edi+00000038h]
  loc_0041B81D: test eax, eax
  loc_0041B81F: fnclex
  loc_0041B821: jge 0041B834h
  loc_0041B823: mov edx, var_98
  loc_0041B829: push 00000038h
  loc_0041B82B: push 004073A0h
  loc_0041B830: push edx
  loc_0041B831: push eax
  loc_0041B832: call __vbaHresultCheckObj
  loc_0041B834: lea eax, var_38
  loc_0041B837: lea ecx, var_34
  loc_0041B83A: push eax
  loc_0041B83B: push ecx
  loc_0041B83C: push 00000002h
  loc_0041B83E: call [00401040h] ; __vbaFreeObjList
  loc_0041B844: mov eax, var_30
  loc_0041B847: add esp, 0000000Ch
  loc_0041B84A: lea ecx, var_34
  loc_0041B84D: mov edx, [eax]
  loc_0041B84F: push ecx
  loc_0041B850: push eax
  loc_0041B851: call [edx+00000054h]
  loc_0041B854: test eax, eax
  loc_0041B856: fnclex
  loc_0041B858: jge 0041B868h
  loc_0041B85A: mov edx, var_30
  loc_0041B85D: push 00000054h
  loc_0041B85F: push 004072E8h
  loc_0041B864: push edx
  loc_0041B865: push eax
  loc_0041B866: call __vbaHresultCheckObj
  loc_0041B868: lea ebx, var_38
  loc_0041B86B: mov eax, var_34
  loc_0041B86E: push ebx
  loc_0041B86F: mov edx, 00000008h
  loc_0041B874: sub esp, 00000010h
  loc_0041B877: mov var_78, edx
  loc_0041B87A: mov ebx, esp
  loc_0041B87C: mov ecx, 00407AACh ; "fldNPLC"
  loc_0041B881: mov var_70, ecx
  loc_0041B884: mov edi, [eax]
  loc_0041B886: mov [ebx], edx
  loc_0041B888: mov edx, var_74
  loc_0041B88B: push eax
  loc_0041B88C: mov var_90, eax
  loc_0041B892: mov [ebx+00000004h], edx
  loc_0041B895: mov [ebx+00000008h], ecx
  loc_0041B898: mov ecx, var_6C
  loc_0041B89B: mov [ebx+0000000Ch], ecx
  loc_0041B89E: call [edi+00000028h]
  loc_0041B8A1: test eax, eax
  loc_0041B8A3: fnclex
  loc_0041B8A5: jge 0041B8B8h
  loc_0041B8A7: mov edx, var_90
  loc_0041B8AD: push 00000028h
  loc_0041B8AF: push 00407390h
  loc_0041B8B4: push edx
  loc_0041B8B5: push eax
  loc_0041B8B6: call __vbaHresultCheckObj
  loc_0041B8B8: mov ecx, NPLC
  loc_0041B8BB: sub esp, 00000010h
  loc_0041B8BE: mov eax, var_38
  loc_0041B8C1: mov ebx, esp
  loc_0041B8C3: mov ecx, [ecx]
  loc_0041B8C5: mov edx, 00000003h
  loc_0041B8CA: mov edi, [eax]
  loc_0041B8CC: mov [ebx], edx
  loc_0041B8CE: mov edx, var_84
  loc_0041B8D4: push eax
  loc_0041B8D5: mov [ebx+00000004h], edx
  loc_0041B8D8: mov var_98, eax
  loc_0041B8DE: mov [ebx+00000008h], ecx
  loc_0041B8E1: mov ecx, var_7C
  loc_0041B8E4: mov [ebx+0000000Ch], ecx
  loc_0041B8E7: call [edi+00000038h]
  loc_0041B8EA: test eax, eax
  loc_0041B8EC: fnclex
  loc_0041B8EE: jge 0041B901h
  loc_0041B8F0: mov edx, var_98
  loc_0041B8F6: push 00000038h
  loc_0041B8F8: push 004073A0h
  loc_0041B8FD: push edx
  loc_0041B8FE: push eax
  loc_0041B8FF: call __vbaHresultCheckObj
  loc_0041B901: lea eax, var_38
  loc_0041B904: lea ecx, var_34
  loc_0041B907: push eax
  loc_0041B908: push ecx
  loc_0041B909: push 00000002h
  loc_0041B90B: call [00401040h] ; __vbaFreeObjList
  loc_0041B911: mov ecx, 0000000Ah
  loc_0041B916: mov eax, 80020004h
  loc_0041B91B: push ecx
  loc_0041B91C: mov var_78, ecx
  loc_0041B91F: mov ebx, esp
  loc_0041B921: mov edx, eax
  loc_0041B923: sub esp, 00000010h
  loc_0041B926: mov edi, var_30
  loc_0041B929: mov [ebx], ecx
  loc_0041B92B: mov ecx, var_84
  loc_0041B931: mov var_70, edx
  loc_0041B934: mov edi, [edi]
  loc_0041B936: mov [ebx+00000004h], ecx
  loc_0041B939: mov ecx, esp
  loc_0041B93B: mov [ebx+00000008h], eax
  loc_0041B93E: mov eax, var_7C
  loc_0041B941: mov [ebx+0000000Ch], eax
  loc_0041B944: mov eax, var_78
  loc_0041B947: mov [ecx], eax
  loc_0041B949: mov eax, var_74
  loc_0041B94C: mov [ecx+00000004h], eax
  loc_0041B94F: mov eax, var_30
  loc_0041B952: push eax
  loc_0041B953: mov [ecx+00000008h], edx
  loc_0041B956: mov edx, var_6C
  loc_0041B959: mov [ecx+0000000Ch], edx
  loc_0041B95C: call [edi+000000ACh]
  loc_0041B962: test eax, eax
  loc_0041B964: fnclex
  loc_0041B966: jge 0041B979h
  loc_0041B968: mov ecx, var_30
  loc_0041B96B: push 000000ACh
  loc_0041B970: push 004072E8h
  loc_0041B975: push ecx
  loc_0041B976: push eax
  loc_0041B977: call __vbaHresultCheckObj
  loc_0041B979: mov eax, var_30
  loc_0041B97C: push eax
  loc_0041B97D: mov edx, [eax]
  loc_0041B97F: call [edx+00000080h]
  loc_0041B985: test eax, eax
  loc_0041B987: fnclex
  loc_0041B989: jge 0041B99Ch
  loc_0041B98B: mov ecx, var_30
  loc_0041B98E: push 00000080h
  loc_0041B993: push 004072E8h
  loc_0041B998: push ecx
  loc_0041B999: push eax
  loc_0041B99A: call __vbaHresultCheckObj
  loc_0041B99C: push 0040713Ch
  loc_0041B9A1: push 00000000h
  loc_0041B9A3: call [004011D4h] ; __vbaCastObj
  loc_0041B9A9: lea edx, var_30
  loc_0041B9AC: push eax
  loc_0041B9AD: push edx
  loc_0041B9AE: call [00401080h] ; __vbaObjSet
  loc_0041B9B4: call [004010A0h] ; rtcDoEvents
  loc_0041B9BA: fwait
  loc_0041B9BB: push 0041BA0Ch
  loc_0041B9C0: jmp 0041B9F9h
  loc_0041B9C2: test var_4, 04h
  loc_0041B9C6: jz 0041B9D1h
  loc_0041B9C8: lea ecx, var_28
  loc_0041B9CB: call [00401020h] ; __vbaFreeVar
  loc_0041B9D1: lea eax, var_38
  loc_0041B9D4: lea ecx, var_34
  loc_0041B9D7: push eax
  loc_0041B9D8: push ecx
  loc_0041B9D9: push 00000002h
  loc_0041B9DB: call [00401040h] ; __vbaFreeObjList
  loc_0041B9E1: lea edx, var_68
  loc_0041B9E4: lea eax, var_58
  loc_0041B9E7: push edx
  loc_0041B9E8: lea ecx, var_48
  loc_0041B9EB: push eax
  loc_0041B9EC: push ecx
  loc_0041B9ED: push 00000003h
  loc_0041B9EF: call [00401038h] ; __vbaFreeVarList
  loc_0041B9F5: add esp, 0000001Ch
  loc_0041B9F8: ret
  loc_0041B9F9: lea ecx, var_2C
  loc_0041B9FC: call [004011F4h] ; __vbaFreeStr
  loc_0041BA02: lea ecx, var_30
  loc_0041BA05: call [004011F0h] ; __vbaFreeObj
  loc_0041BA0B: ret
  loc_0041BA0C: mov eax, Me
  loc_0041BA0F: push eax
  loc_0041BA10: mov edx, [eax]
  loc_0041BA12: call [edx+00000008h]
  loc_0041BA15: mov eax, arg_38
  loc_0041BA18: mov ecx, var_28
  loc_0041BA1B: mov edx, var_24
  loc_0041BA1E: mov [eax], ecx
  loc_0041BA20: mov ecx, var_20
  loc_0041BA23: mov [eax+00000004h], edx
  loc_0041BA26: mov edx, var_1C
  loc_0041BA29: mov [eax+00000008h], ecx
  loc_0041BA2C: mov [eax+0000000Ch], edx
  loc_0041BA2F: mov eax, var_4
  loc_0041BA32: mov ecx, var_14
  loc_0041BA35: pop edi
  loc_0041BA36: pop esi
  loc_0041BA37: mov fs:[00000000h], ecx
  loc_0041BA3E: pop ebx
  loc_0041BA3F: mov esp, ebp
  loc_0041BA41: pop ebp
  loc_0041BA42: retn 0034h
End Function

Public Function WriteTxtDataToDisplay(ParamNewText) '41BA50
  loc_0041BA50: push ebp
  loc_0041BA51: mov ebp, esp
  loc_0041BA53: sub esp, 0000000Ch
  loc_0041BA56: push 00401AA6h ; __vbaExceptHandler
  loc_0041BA5B: mov eax, fs:[00000000h]
  loc_0041BA61: push eax
  loc_0041BA62: mov fs:[00000000h], esp
  loc_0041BA69: sub esp, 000000FCh
  loc_0041BA6F: push ebx
  loc_0041BA70: push esi
  loc_0041BA71: push edi
  loc_0041BA72: mov var_C, esp
  loc_0041BA75: mov var_8, 00401660h
  loc_0041BA7C: xor edi, edi
  loc_0041BA7E: mov var_4, edi
  loc_0041BA81: mov ebx, Me
  loc_0041BA84: push ebx
  loc_0041BA85: mov eax, [ebx]
  loc_0041BA87: call [eax+00000004h]
  loc_0041BA8A: mov ecx, arg_10
  loc_0041BA8D: push ebx
  loc_0041BA8E: mov var_1C, edi
  loc_0041BA91: mov var_2C, edi
  loc_0041BA94: mov [ecx], edi
  loc_0041BA96: mov edx, [ebx]
  loc_0041BA98: mov var_30, edi
  loc_0041BA9B: mov var_34, edi
  loc_0041BA9E: mov var_44, edi
  loc_0041BAA1: mov var_54, edi
  loc_0041BAA4: mov var_64, edi
  loc_0041BAA7: mov var_74, edi
  loc_0041BAAA: mov var_84, edi
  loc_0041BAB0: mov var_94, edi
  loc_0041BAB6: mov var_A4, edi
  loc_0041BABC: mov var_B4, edi
  loc_0041BAC2: mov var_C4, edi
  loc_0041BAC8: mov var_D4, edi
  loc_0041BACE: mov var_E4, edi
  loc_0041BAD4: mov var_F4, edi
  loc_0041BADA: call [edx+0000035Ch]
  loc_0041BAE0: push eax
  loc_0041BAE1: lea eax, var_34
  loc_0041BAE4: push eax
  loc_0041BAE5: call [00401080h] ; __vbaObjSet
  loc_0041BAEB: mov esi, eax
  loc_0041BAED: lea edx, var_30
  loc_0041BAF0: push edx
  loc_0041BAF1: push esi
  loc_0041BAF2: mov ecx, [esi]
  loc_0041BAF4: call [ecx+000000A0h]
  loc_0041BAFA: cmp eax, edi
  loc_0041BAFC: fnclex
  loc_0041BAFE: jge 0041BB12h
  loc_0041BB00: push 000000A0h
  loc_0041BB05: push 00405398h
  loc_0041BB0A: push esi
  loc_0041BB0B: push eax
  loc_0041BB0C: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041BB12: mov edx, var_30
  loc_0041BB15: lea ecx, var_1C
  loc_0041BB18: mov var_30, edi
  loc_0041BB1B: call [004011D0h] ; __vbaStrMove
  loc_0041BB21: lea ecx, var_34
  loc_0041BB24: call [004011F0h] ; __vbaFreeObj
  loc_0041BB2A: mov eax, var_1C
  loc_0041BB2D: mov esi, [0040102Ch] ; __vbaLenBstr
  loc_0041BB33: push eax
  loc_0041BB34: call __vbaLenBstr
  loc_0041BB36: cmp eax, 000003E8h
  loc_0041BB3B: jle 0041BC2Dh
  loc_0041BB41: mov ecx, var_1C
  loc_0041BB44: push ecx
  loc_0041BB45: call __vbaLenBstr
  loc_0041BB47: mov esi, eax
  loc_0041BB49: sub esi, 00000001h
  loc_0041BB4C: jo 0041BEC1h
  loc_0041BB52: mov eax, 00000001h
  loc_0041BB57: cmp esi, eax
  loc_0041BB59: jl 0041BBE1h
  loc_0041BB5F: mov var_3C, eax
  loc_0041BB62: lea edx, var_1C
  loc_0041BB65: lea eax, var_44
  loc_0041BB68: mov var_AC, edx
  loc_0041BB6E: push eax
  loc_0041BB6F: lea ecx, var_B4
  loc_0041BB75: push esi
  loc_0041BB76: lea edx, var_54
  loc_0041BB79: push ecx
  loc_0041BB7A: push edx
  loc_0041BB7B: mov var_44, 00000002h
  loc_0041BB82: mov var_B4, 00004008h
  loc_0041BB8C: call [004010BCh] ; rtcMidCharVar
  loc_0041BB92: lea eax, var_64
  loc_0041BB95: push 0000000Ah
  loc_0041BB97: push eax
  loc_0041BB98: call [0040113Ch] ; rtcVarBstrFromAnsi
  loc_0041BB9E: lea ecx, var_54
  loc_0041BBA1: lea edx, var_64
  loc_0041BBA4: push ecx
  loc_0041BBA5: push edx
  loc_0041BBA6: call [004010E4h] ; __vbaVarTstEq
  loc_0041BBAC: mov di, ax
  loc_0041BBAF: lea eax, var_64
  loc_0041BBB2: lea ecx, var_54
  loc_0041BBB5: push eax
  loc_0041BBB6: lea edx, var_44
  loc_0041BBB9: push ecx
  loc_0041BBBA: push edx
  loc_0041BBBB: push 00000003h
  loc_0041BBBD: call [00401038h] ; __vbaFreeVarList
  loc_0041BBC3: add esp, 00000010h
  loc_0041BBC6: test di, di
  loc_0041BBC9: jnz 0041BBDFh
  loc_0041BBCB: or eax, FFFFFFFFh
  loc_0041BBCE: add eax, esi
  loc_0041BBD0: jo 0041BEC1h
  loc_0041BBD6: mov esi, eax
  loc_0041BBD8: xor edi, edi
  loc_0041BBDA: jmp 0041BB52h
  loc_0041BBDF: xor edi, edi
  loc_0041BBE1: cmp esi, edi
  loc_0041BBE3: jnz 0041BBEAh
  loc_0041BBE5: mov esi, 00000320h
  loc_0041BBEA: lea ecx, var_B4
  loc_0041BBF0: push esi
  loc_0041BBF1: lea edx, var_44
  loc_0041BBF4: lea eax, var_1C
  loc_0041BBF7: push ecx
  loc_0041BBF8: push edx
  loc_0041BBF9: mov var_AC, eax
  loc_0041BBFF: mov var_B4, 00004008h
  loc_0041BC09: call [004011C4h] ; rtcLeftCharVar
  loc_0041BC0F: lea eax, var_44
  loc_0041BC12: push eax
  loc_0041BC13: call [00401030h] ; __vbaStrVarMove
  loc_0041BC19: mov edx, eax
  loc_0041BC1B: lea ecx, var_1C
  loc_0041BC1E: call [004011D0h] ; __vbaStrMove
  loc_0041BC24: lea ecx, var_44
  loc_0041BC27: call [00401020h] ; __vbaFreeVar
  loc_0041BC2D: lea ecx, var_44
  loc_0041BC30: push ecx
  loc_0041BC31: call [004011E4h] ; rtcGetPresentDate
  loc_0041BC37: mov esi, 00000008h
  loc_0041BC3C: lea edx, var_B4
  loc_0041BC42: lea ecx, var_54
  loc_0041BC45: mov var_AC, 00407AC0h ; "m/d/yy h:mm:ss"
  loc_0041BC4F: mov var_B4, esi
  loc_0041BC55: call [004011B4h] ; __vbaVarDup
  loc_0041BC5B: push 00000001h
  loc_0041BC5D: lea edx, var_54
  loc_0041BC60: push 00000001h
  loc_0041BC62: lea eax, var_44
  loc_0041BC65: push edx
  loc_0041BC66: lea ecx, var_64
  loc_0041BC69: push eax
  loc_0041BC6A: push ecx
  loc_0041BC6B: call [00401054h] ; rtcVarFromFormatVar
  loc_0041BC71: mov edx, ParamNewText
  loc_0041BC74: mov ecx, var_1C
  loc_0041BC77: mov var_EC, ecx
  loc_0041BC7D: lea ecx, var_74
  loc_0041BC80: mov eax, [edx]
  loc_0041BC82: lea edx, var_64
  loc_0041BC85: mov var_CC, eax
  loc_0041BC8B: lea eax, var_C4
  loc_0041BC91: push edx
  loc_0041BC92: mov var_C4, esi
  loc_0041BC98: mov var_D4, esi
  loc_0041BC9E: mov var_E4, esi
  loc_0041BCA4: mov var_F4, esi
  loc_0041BCAA: mov esi, [004011ACh] ; __vbaVarAdd
  loc_0041BCB0: push eax
  loc_0041BCB1: push ecx
  loc_0041BCB2: mov var_BC, 00407AE4h ; "   "
  loc_0041BCBC: mov var_DC, 004054D8h ; vbCrLf
  loc_0041BCC6: call __vbaVarAdd
  loc_0041BCC8: push eax
  loc_0041BCC9: lea edx, var_D4
  loc_0041BCCF: lea eax, var_84
  loc_0041BCD5: push edx
  loc_0041BCD6: push eax
  loc_0041BCD7: call __vbaVarAdd
  loc_0041BCD9: lea ecx, var_E4
  loc_0041BCDF: push eax
  loc_0041BCE0: lea edx, var_94
  loc_0041BCE6: push ecx
  loc_0041BCE7: push edx
  loc_0041BCE8: call __vbaVarAdd
  loc_0041BCEA: push eax
  loc_0041BCEB: lea eax, var_F4
  loc_0041BCF1: lea ecx, var_A4
  loc_0041BCF7: push eax
  loc_0041BCF8: push ecx
  loc_0041BCF9: call __vbaVarAdd
  loc_0041BCFB: push eax
  loc_0041BCFC: call [00401030h] ; __vbaStrVarMove
  loc_0041BD02: mov edx, eax
  loc_0041BD04: lea ecx, var_1C
  loc_0041BD07: call [004011D0h] ; __vbaStrMove
  loc_0041BD0D: lea edx, var_A4
  loc_0041BD13: lea eax, var_94
  loc_0041BD19: push edx
  loc_0041BD1A: lea ecx, var_84
  loc_0041BD20: push eax
  loc_0041BD21: lea edx, var_74
  loc_0041BD24: push ecx
  loc_0041BD25: lea eax, var_64
  loc_0041BD28: push edx
  loc_0041BD29: lea ecx, var_54
  loc_0041BD2C: push eax
  loc_0041BD2D: lea edx, var_44
  loc_0041BD30: push ecx
  loc_0041BD31: push edx
  loc_0041BD32: push 00000007h
  loc_0041BD34: call [00401038h] ; __vbaFreeVarList
  loc_0041BD3A: mov eax, [ebx]
  loc_0041BD3C: add esp, 00000020h
  loc_0041BD3F: push ebx
  loc_0041BD40: call [eax+0000035Ch]
  loc_0041BD46: push eax
  loc_0041BD47: lea ecx, var_34
  loc_0041BD4A: push ecx
  loc_0041BD4B: call [00401080h] ; __vbaObjSet
  loc_0041BD51: mov esi, eax
  loc_0041BD53: push edi
  loc_0041BD54: push esi
  loc_0041BD55: mov edx, [esi]
  loc_0041BD57: call [edx+000001B4h]
  loc_0041BD5D: cmp eax, edi
  loc_0041BD5F: fnclex
  loc_0041BD61: jge 0041BD75h
  loc_0041BD63: push 000001B4h
  loc_0041BD68: push 00405398h
  loc_0041BD6D: push esi
  loc_0041BD6E: push eax
  loc_0041BD6F: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041BD75: lea ecx, var_34
  loc_0041BD78: call [004011F0h] ; __vbaFreeObj
  loc_0041BD7E: mov eax, [ebx]
  loc_0041BD80: push ebx
  loc_0041BD81: call [eax+0000035Ch]
  loc_0041BD87: lea ecx, var_34
  loc_0041BD8A: push eax
  loc_0041BD8B: push ecx
  loc_0041BD8C: call [00401080h] ; __vbaObjSet
  loc_0041BD92: mov esi, eax
  loc_0041BD94: mov eax, var_1C
  loc_0041BD97: push eax
  loc_0041BD98: push esi
  loc_0041BD99: mov edx, [esi]
  loc_0041BD9B: call [edx+000000A4h]
  loc_0041BDA1: cmp eax, edi
  loc_0041BDA3: fnclex
  loc_0041BDA5: jge 0041BDB9h
  loc_0041BDA7: push 000000A4h
  loc_0041BDAC: push 00405398h
  loc_0041BDB1: push esi
  loc_0041BDB2: push eax
  loc_0041BDB3: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041BDB9: mov esi, [004011F0h] ; __vbaFreeObj
  loc_0041BDBF: lea ecx, var_34
  loc_0041BDC2: call __vbaFreeObj
  loc_0041BDC4: mov ecx, [ebx]
  loc_0041BDC6: push ebx
  loc_0041BDC7: call [ecx+0000035Ch]
  loc_0041BDCD: lea edx, var_34
  loc_0041BDD0: push eax
  loc_0041BDD1: push edx
  loc_0041BDD2: call [00401080h] ; __vbaObjSet
  loc_0041BDD8: mov ebx, eax
  loc_0041BDDA: push FFFFFFFFh
  loc_0041BDDC: push ebx
  loc_0041BDDD: mov eax, [ebx]
  loc_0041BDDF: call [eax+000001B4h]
  loc_0041BDE5: cmp eax, edi
  loc_0041BDE7: fnclex
  loc_0041BDE9: jge 0041BDFDh
  loc_0041BDEB: push 000001B4h
  loc_0041BDF0: push 00405398h
  loc_0041BDF5: push ebx
  loc_0041BDF6: push eax
  loc_0041BDF7: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041BDFD: lea ecx, var_34
  loc_0041BE00: call __vbaFreeObj
  loc_0041BE02: lea edx, var_B4
  loc_0041BE08: lea ecx, var_2C
  loc_0041BE0B: mov var_AC, FFFFFFFFh
  loc_0041BE15: mov var_B4, 0000000Bh
  loc_0041BE1F: call [00401014h] ; __vbaVarMove
  loc_0041BE25: push 0041BE88h
  loc_0041BE2A: jmp 0041BE7Eh
  loc_0041BE2C: test var_4, 04h
  loc_0041BE30: jz 0041BE3Bh
  loc_0041BE32: lea ecx, var_2C
  loc_0041BE35: call [00401020h] ; __vbaFreeVar
  loc_0041BE3B: lea ecx, var_30
  loc_0041BE3E: call [004011F4h] ; __vbaFreeStr
  loc_0041BE44: lea ecx, var_34
  loc_0041BE47: call [004011F0h] ; __vbaFreeObj
  loc_0041BE4D: lea ecx, var_A4
  loc_0041BE53: lea edx, var_94
  loc_0041BE59: push ecx
  loc_0041BE5A: lea eax, var_84
  loc_0041BE60: push edx
  loc_0041BE61: lea ecx, var_74
  loc_0041BE64: push eax
  loc_0041BE65: lea edx, var_64
  loc_0041BE68: push ecx
  loc_0041BE69: lea eax, var_54
  loc_0041BE6C: push edx
  loc_0041BE6D: lea ecx, var_44
  loc_0041BE70: push eax
  loc_0041BE71: push ecx
  loc_0041BE72: push 00000007h
  loc_0041BE74: call [00401038h] ; __vbaFreeVarList
  loc_0041BE7A: add esp, 00000020h
  loc_0041BE7D: ret
  loc_0041BE7E: lea ecx, var_1C
  loc_0041BE81: call [004011F4h] ; __vbaFreeStr
  loc_0041BE87: ret
  loc_0041BE88: mov eax, Me
  loc_0041BE8B: push eax
  loc_0041BE8C: mov edx, [eax]
  loc_0041BE8E: call [edx+00000008h]
  loc_0041BE91: mov eax, arg_10
  loc_0041BE94: mov ecx, var_2C
  loc_0041BE97: mov edx, var_28
  loc_0041BE9A: mov [eax], ecx
  loc_0041BE9C: mov ecx, var_24
  loc_0041BE9F: mov [eax+00000004h], edx
  loc_0041BEA2: mov edx, var_20
  loc_0041BEA5: mov [eax+00000008h], ecx
  loc_0041BEA8: mov [eax+0000000Ch], edx
  loc_0041BEAB: mov eax, var_4
  loc_0041BEAE: mov ecx, var_14
  loc_0041BEB1: pop edi
  loc_0041BEB2: pop esi
  loc_0041BEB3: mov fs:[00000000h], ecx
  loc_0041BEBA: pop ebx
  loc_0041BEBB: mov esp, ebp
  loc_0041BEBD: pop ebp
  loc_0041BEBE: retn 000Ch
End Function

Public Function RunCancel(arg_C) '41BED0
  loc_0041BED0: push ebp
  loc_0041BED1: mov ebp, esp
  loc_0041BED3: sub esp, 0000000Ch
  loc_0041BED6: push 00401AA6h ; __vbaExceptHandler
  loc_0041BEDB: mov eax, fs:[00000000h]
  loc_0041BEE1: push eax
  loc_0041BEE2: mov fs:[00000000h], esp
  loc_0041BEE9: sub esp, 00000024h
  loc_0041BEEC: push ebx
  loc_0041BEED: push esi
  loc_0041BEEE: push edi
  loc_0041BEEF: mov var_C, esp
  loc_0041BEF2: mov var_8, 00401670h
  loc_0041BEF9: xor ebx, ebx
  loc_0041BEFB: mov var_4, ebx
  loc_0041BEFE: mov esi, Me
  loc_0041BF01: push esi
  loc_0041BF02: mov eax, [esi]
  loc_0041BF04: call [eax+00000004h]
  loc_0041BF07: mov ecx, arg_C
  loc_0041BF0A: push esi
  loc_0041BF0B: mov var_24, ebx
  loc_0041BF0E: mov var_28, ebx
  loc_0041BF11: mov [ecx], ebx
  loc_0041BF13: mov edx, [esi]
  loc_0041BF15: call [edx+00000390h]
  loc_0041BF1B: push eax
  loc_0041BF1C: lea eax, var_28
  loc_0041BF1F: push eax
  loc_0041BF20: call [00401080h] ; __vbaObjSet
  loc_0041BF26: mov edi, eax
  loc_0041BF28: push 00406C50h ; "GO"
  loc_0041BF2D: push edi
  loc_0041BF2E: mov ecx, [edi]
  loc_0041BF30: call [ecx+00000054h]
  loc_0041BF33: cmp eax, ebx
  loc_0041BF35: fnclex
  loc_0041BF37: jge 0041BF48h
  loc_0041BF39: push 00000054h
  loc_0041BF3B: push 00406128h
  loc_0041BF40: push edi
  loc_0041BF41: push eax
  loc_0041BF42: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041BF48: mov ebx, [004011F0h] ; __vbaFreeObj
  loc_0041BF4E: lea ecx, var_28
  loc_0041BF51: call ebx
  loc_0041BF53: mov edx, [esi]
  loc_0041BF55: push esi
  loc_0041BF56: call [edx+0000039Ch]
  loc_0041BF5C: push eax
  loc_0041BF5D: lea eax, var_28
  loc_0041BF60: push eax
  loc_0041BF61: call [00401080h] ; __vbaObjSet
  loc_0041BF67: mov edi, eax
  loc_0041BF69: push 004078E0h ; "Run cancelled by user"
  loc_0041BF6E: push edi
  loc_0041BF6F: mov ecx, [edi]
  loc_0041BF71: call [ecx+00000054h]
  loc_0041BF74: test eax, eax
  loc_0041BF76: fnclex
  loc_0041BF78: jge 0041BF89h
  loc_0041BF7A: push 00000054h
  loc_0041BF7C: push 0040575Ch
  loc_0041BF81: push edi
  loc_0041BF82: push eax
  loc_0041BF83: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041BF89: lea ecx, var_28
  loc_0041BF8C: call ebx
  loc_0041BF8E: mov edx, [esi]
  loc_0041BF90: push 00000000h
  loc_0041BF92: push esi
  loc_0041BF93: call [edx+000000A4h]
  loc_0041BF99: test eax, eax
  loc_0041BF9B: fnclex
  loc_0041BF9D: jge 0041BFB1h
  loc_0041BF9F: push 000000A4h
  loc_0041BFA4: push 0040576Ch
  loc_0041BFA9: push esi
  loc_0041BFAA: push eax
  loc_0041BFAB: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041BFB1: push 0041BFD2h
  loc_0041BFB6: jmp 0041BFD1h
  loc_0041BFB8: test var_4, 04h
  loc_0041BFBC: jz 0041BFC7h
  loc_0041BFBE: lea ecx, var_24
  loc_0041BFC1: call [00401020h] ; __vbaFreeVar
  loc_0041BFC7: lea ecx, var_28
  loc_0041BFCA: call [004011F0h] ; __vbaFreeObj
  loc_0041BFD0: ret
  loc_0041BFD1: ret
  loc_0041BFD2: mov eax, Me
  loc_0041BFD5: push eax
  loc_0041BFD6: mov ecx, [eax]
  loc_0041BFD8: call [ecx+00000008h]
  loc_0041BFDB: mov edx, arg_C
  loc_0041BFDE: mov eax, var_24
  loc_0041BFE1: mov ecx, var_20
  loc_0041BFE4: mov [edx], eax
  loc_0041BFE6: mov eax, var_1C
  loc_0041BFE9: mov [edx+00000004h], ecx
  loc_0041BFEC: mov ecx, var_18
  loc_0041BFEF: mov [edx+00000008h], eax
  loc_0041BFF2: mov [edx+0000000Ch], ecx
  loc_0041BFF5: mov eax, var_4
  loc_0041BFF8: mov ecx, var_14
  loc_0041BFFB: pop edi
  loc_0041BFFC: pop esi
  loc_0041BFFD: mov fs:[00000000h], ecx
  loc_0041C004: pop ebx
  loc_0041C005: mov esp, ebp
  loc_0041C007: pop ebp
  loc_0041C008: retn 0008h
End Function

Public Function CloseUpdbSave(TestSerial) '41C010
  loc_0041C010: push ebp
  loc_0041C011: mov ebp, esp
  loc_0041C013: sub esp, 0000000Ch
  loc_0041C016: push 00401AA6h ; __vbaExceptHandler
  loc_0041C01B: mov eax, fs:[00000000h]
  loc_0041C021: push eax
  loc_0041C022: mov fs:[00000000h], esp
  loc_0041C029: sub esp, 00000078h
  loc_0041C02C: push ebx
  loc_0041C02D: push esi
  loc_0041C02E: push edi
  loc_0041C02F: mov var_C, esp
  loc_0041C032: mov var_8, 00401680h
  loc_0041C039: xor edi, edi
  loc_0041C03B: mov var_4, edi
  loc_0041C03E: mov eax, Me
  loc_0041C041: push eax
  loc_0041C042: mov ecx, [eax]
  loc_0041C044: call [ecx+00000004h]
  loc_0041C047: mov edx, arg_10
  loc_0041C04A: mov var_18, edi
  loc_0041C04D: mov var_1C, edi
  loc_0041C050: mov var_2C, edi
  loc_0041C053: mov [edx], edi
  loc_0041C055: cmp [0042303Eh], di
  loc_0041C05C: mov var_30, edi
  loc_0041C05F: mov var_34, edi
  loc_0041C062: mov var_38, edi
  loc_0041C065: mov var_48, edi
  loc_0041C068: mov var_58, edi
  loc_0041C06B: mov var_68, edi
  loc_0041C06E: mov var_6C, edi
  loc_0041C071: mov var_70, edi
  loc_0041C074: jnz 0041C349h
  loc_0041C07A: mov eax, TestSerial
  loc_0041C07D: push 0040775Ch ; "SELECT * FROM tblLampElectricalTest WHERE tblLampElectricalTest.fldTestSerial = "
  loc_0041C082: mov ecx, [eax]
  loc_0041C084: push ecx
  loc_0041C085: call [00401018h] ; __vbaStrI4
  loc_0041C08B: mov esi, [004011D0h] ; __vbaStrMove
  loc_0041C091: mov edx, eax
  loc_0041C093: lea ecx, var_30
  loc_0041C096: call __vbaStrMove
  loc_0041C098: push eax
  loc_0041C099: call [00401050h] ; __vbaStrCat
  loc_0041C09F: mov edx, eax
  loc_0041C0A1: lea ecx, var_18
  loc_0041C0A4: call __vbaStrMove
  loc_0041C0A6: lea ecx, var_30
  loc_0041C0A9: call [004011F4h] ; __vbaFreeStr
  loc_0041C0AF: push 0040714Ch
  loc_0041C0B4: call [00401110h] ; __vbaNew
  loc_0041C0BA: lea edx, var_1C
  loc_0041C0BD: push eax
  loc_0041C0BE: push edx
  loc_0041C0BF: call [00401080h] ; __vbaObjSet
  loc_0041C0C5: mov eax, var_1C
  loc_0041C0C8: push 00000002h
  loc_0041C0CA: push eax
  loc_0041C0CB: mov ecx, [eax]
  loc_0041C0CD: call [ecx+0000004Ch]
  loc_0041C0D0: cmp eax, edi
  loc_0041C0D2: fnclex
  loc_0041C0D4: jge 0041C0E8h
  loc_0041C0D6: mov edx, var_1C
  loc_0041C0D9: push 0000004Ch
  loc_0041C0DB: push 004072E8h
  loc_0041C0E0: push edx
  loc_0041C0E1: push eax
  loc_0041C0E2: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041C0E8: mov eax, var_1C
  loc_0041C0EB: push 00000003h
  loc_0041C0ED: push eax
  loc_0041C0EE: mov ecx, [eax]
  loc_0041C0F0: call [ecx+0000005Ch]
  loc_0041C0F3: cmp eax, edi
  loc_0041C0F5: fnclex
  loc_0041C0F7: jge 0041C10Bh
  loc_0041C0F9: mov edx, var_1C
  loc_0041C0FC: push 0000005Ch
  loc_0041C0FE: push 004072E8h
  loc_0041C103: push edx
  loc_0041C104: push eax
  loc_0041C105: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041C10B: push FFFFFFFFh
  loc_0041C10D: push FFFFFFFFh
  loc_0041C10F: push FFFFFFFFh
  loc_0041C111: mov eax, [00423028h]
  loc_0041C116: sub esp, 00000010h
  loc_0041C119: mov ecx, 00000009h
  loc_0041C11E: mov ebx, esp
  loc_0041C120: sub esp, 00000010h
  loc_0041C123: mov edx, var_18
  loc_0041C126: mov edi, var_1C
  loc_0041C129: mov [ebx], ecx
  loc_0041C12B: mov ecx, var_64
  loc_0041C12E: mov esi, 00000008h
  loc_0041C133: mov edi, [edi]
  loc_0041C135: mov [ebx+00000004h], ecx
  loc_0041C138: mov ecx, esp
  loc_0041C13A: mov [ebx+00000008h], eax
  loc_0041C13D: mov eax, var_5C
  loc_0041C140: mov [ebx+0000000Ch], eax
  loc_0041C143: mov eax, var_54
  loc_0041C146: mov [ecx], esi
  loc_0041C148: mov [ecx+00000004h], eax
  loc_0041C14B: mov eax, var_1C
  loc_0041C14E: push eax
  loc_0041C14F: mov [ecx+00000008h], edx
  loc_0041C152: mov edx, var_4C
  loc_0041C155: mov [ecx+0000000Ch], edx
  loc_0041C158: call [edi+000000A0h]
  loc_0041C15E: test eax, eax
  loc_0041C160: fnclex
  loc_0041C162: jge 0041C17Dh
  loc_0041C164: mov ecx, var_1C
  loc_0041C167: mov esi, [0040105Ch] ; __vbaHresultCheckObj
  loc_0041C16D: push 000000A0h
  loc_0041C172: push 004072E8h
  loc_0041C177: push ecx
  loc_0041C178: push eax
  loc_0041C179: call __vbaHresultCheckObj
  loc_0041C17B: jmp 0041C183h
  loc_0041C17D: mov esi, [0040105Ch] ; __vbaHresultCheckObj
  loc_0041C183: mov eax, var_1C
  loc_0041C186: lea ecx, var_6C
  loc_0041C189: push ecx
  loc_0041C18A: push eax
  loc_0041C18B: mov edx, [eax]
  loc_0041C18D: call [edx+00000050h]
  loc_0041C190: test eax, eax
  loc_0041C192: fnclex
  loc_0041C194: jge 0041C1A4h
  loc_0041C196: mov edx, var_1C
  loc_0041C199: push 00000050h
  loc_0041C19B: push 004072E8h
  loc_0041C1A0: push edx
  loc_0041C1A1: push eax
  loc_0041C1A2: call __vbaHresultCheckObj
  loc_0041C1A4: mov eax, var_1C
  loc_0041C1A7: lea edx, var_70
  loc_0041C1AA: push edx
  loc_0041C1AB: push eax
  loc_0041C1AC: mov ecx, [eax]
  loc_0041C1AE: call [ecx+00000034h]
  loc_0041C1B1: test eax, eax
  loc_0041C1B3: fnclex
  loc_0041C1B5: jge 0041C1C5h
  loc_0041C1B7: mov ecx, var_1C
  loc_0041C1BA: push 00000034h
  loc_0041C1BC: push 004072E8h
  loc_0041C1C1: push ecx
  loc_0041C1C2: push eax
  loc_0041C1C3: call __vbaHresultCheckObj
  loc_0041C1C5: xor edx, edx
  loc_0041C1C7: cmp var_70, dx
  loc_0041C1CB: setz dl
  loc_0041C1CE: xor eax, eax
  loc_0041C1D0: cmp var_6C, ax
  loc_0041C1D4: setz al
  loc_0041C1D7: or edx, eax
  loc_0041C1D9: jz 0041C30Eh
  loc_0041C1DF: mov eax, var_1C
  loc_0041C1E2: lea edx, var_34
  loc_0041C1E5: push edx
  loc_0041C1E6: push eax
  loc_0041C1E7: mov ecx, [eax]
  loc_0041C1E9: call [ecx+00000054h]
  loc_0041C1EC: test eax, eax
  loc_0041C1EE: fnclex
  loc_0041C1F0: jge 0041C200h
  loc_0041C1F2: mov ecx, var_1C
  loc_0041C1F5: push 00000054h
  loc_0041C1F7: push 004072E8h
  loc_0041C1FC: push ecx
  loc_0041C1FD: push eax
  loc_0041C1FE: call __vbaHresultCheckObj
  loc_0041C200: lea ebx, var_38
  loc_0041C203: mov eax, var_34
  loc_0041C206: push ebx
  loc_0041C207: mov edx, 00000008h
  loc_0041C20C: sub esp, 00000010h
  loc_0041C20F: mov edi, [eax]
  loc_0041C211: mov ebx, esp
  loc_0041C213: mov ecx, 00407910h ; "fldEndDate"
  loc_0041C218: push eax
  loc_0041C219: mov var_78, eax
  loc_0041C21C: mov [ebx], edx
  loc_0041C21E: mov edx, var_54
  loc_0041C221: mov [ebx+00000004h], edx
  loc_0041C224: mov [ebx+00000008h], ecx
  loc_0041C227: mov ecx, var_4C
  loc_0041C22A: mov [ebx+0000000Ch], ecx
  loc_0041C22D: call [edi+00000028h]
  loc_0041C230: test eax, eax
  loc_0041C232: fnclex
  loc_0041C234: jge 0041C244h
  loc_0041C236: mov edx, var_78
  loc_0041C239: push 00000028h
  loc_0041C23B: push 00407390h
  loc_0041C240: push edx
  loc_0041C241: push eax
  loc_0041C242: call __vbaHresultCheckObj
  loc_0041C244: mov edi, var_38
  loc_0041C247: lea eax, var_48
  loc_0041C24A: push eax
  loc_0041C24B: call [004011E4h] ; rtcGetPresentDate
  loc_0041C251: mov eax, var_48
  loc_0041C254: sub esp, 00000010h
  loc_0041C257: mov edx, esp
  loc_0041C259: mov ecx, [edi]
  loc_0041C25B: push edi
  loc_0041C25C: mov [edx], eax
  loc_0041C25E: mov eax, var_44
  loc_0041C261: mov [edx+00000004h], eax
  loc_0041C264: mov eax, var_40
  loc_0041C267: mov [edx+00000008h], eax
  loc_0041C26A: mov eax, var_3C
  loc_0041C26D: mov [edx+0000000Ch], eax
  loc_0041C270: call [ecx+00000038h]
  loc_0041C273: test eax, eax
  loc_0041C275: fnclex
  loc_0041C277: jge 0041C284h
  loc_0041C279: push 00000038h
  loc_0041C27B: push 004073A0h
  loc_0041C280: push edi
  loc_0041C281: push eax
  loc_0041C282: call __vbaHresultCheckObj
  loc_0041C284: lea ecx, var_38
  loc_0041C287: lea edx, var_34
  loc_0041C28A: push ecx
  loc_0041C28B: push edx
  loc_0041C28C: push 00000002h
  loc_0041C28E: call [00401040h] ; __vbaFreeObjList
  loc_0041C294: add esp, 0000000Ch
  loc_0041C297: lea ecx, var_48
  loc_0041C29A: call [00401020h] ; __vbaFreeVar
  loc_0041C2A0: sub esp, 00000010h
  loc_0041C2A3: mov ecx, 0000000Ah
  loc_0041C2A8: mov ebx, esp
  loc_0041C2AA: mov esi, ecx
  loc_0041C2AC: mov eax, 80020004h
  loc_0041C2B1: sub esp, 00000010h
  loc_0041C2B4: mov [ebx], ecx
  loc_0041C2B6: mov ecx, var_64
  loc_0041C2B9: mov edx, eax
  loc_0041C2BB: mov edi, var_1C
  loc_0041C2BE: mov [ebx+00000004h], ecx
  loc_0041C2C1: mov ecx, esp
  loc_0041C2C3: mov edi, [edi]
  loc_0041C2C5: mov [ebx+00000008h], eax
  loc_0041C2C8: mov eax, var_5C
  loc_0041C2CB: mov [ebx+0000000Ch], eax
  loc_0041C2CE: mov eax, var_54
  loc_0041C2D1: mov [ecx], esi
  loc_0041C2D3: mov [ecx+00000004h], eax
  loc_0041C2D6: mov eax, var_1C
  loc_0041C2D9: push eax
  loc_0041C2DA: mov [ecx+00000008h], edx
  loc_0041C2DD: mov edx, var_4C
  loc_0041C2E0: mov [ecx+0000000Ch], edx
  loc_0041C2E3: call [edi+000000ACh]
  loc_0041C2E9: test eax, eax
  loc_0041C2EB: fnclex
  loc_0041C2ED: jge 0041C308h
  loc_0041C2EF: mov ecx, var_1C
  loc_0041C2F2: mov esi, [0040105Ch] ; __vbaHresultCheckObj
  loc_0041C2F8: push 000000ACh
  loc_0041C2FD: push 004072E8h
  loc_0041C302: push ecx
  loc_0041C303: push eax
  loc_0041C304: call __vbaHresultCheckObj
  loc_0041C306: jmp 0041C30Eh
  loc_0041C308: mov esi, [0040105Ch] ; __vbaHresultCheckObj
  loc_0041C30E: mov eax, var_1C
  loc_0041C311: push eax
  loc_0041C312: mov edx, [eax]
  loc_0041C314: call [edx+00000080h]
  loc_0041C31A: test eax, eax
  loc_0041C31C: fnclex
  loc_0041C31E: jge 0041C331h
  loc_0041C320: mov ecx, var_1C
  loc_0041C323: push 00000080h
  loc_0041C328: push 004072E8h
  loc_0041C32D: push ecx
  loc_0041C32E: push eax
  loc_0041C32F: call __vbaHresultCheckObj
  loc_0041C331: push 0040713Ch
  loc_0041C336: push 00000000h
  loc_0041C338: call [004011D4h] ; __vbaCastObj
  loc_0041C33E: lea edx, var_1C
  loc_0041C341: push eax
  loc_0041C342: push edx
  loc_0041C343: call [00401080h] ; __vbaObjSet
  loc_0041C349: push 0041C398h
  loc_0041C34E: jmp 0041C385h
  loc_0041C350: test var_4, 04h
  loc_0041C354: jz 0041C35Fh
  loc_0041C356: lea ecx, var_2C
  loc_0041C359: call [00401020h] ; __vbaFreeVar
  loc_0041C35F: lea ecx, var_30
  loc_0041C362: call [004011F4h] ; __vbaFreeStr
  loc_0041C368: lea eax, var_38
  loc_0041C36B: lea ecx, var_34
  loc_0041C36E: push eax
  loc_0041C36F: push ecx
  loc_0041C370: push 00000002h
  loc_0041C372: call [00401040h] ; __vbaFreeObjList
  loc_0041C378: add esp, 0000000Ch
  loc_0041C37B: lea ecx, var_48
  loc_0041C37E: call [00401020h] ; __vbaFreeVar
  loc_0041C384: ret
  loc_0041C385: lea ecx, var_18
  loc_0041C388: call [004011F4h] ; __vbaFreeStr
  loc_0041C38E: lea ecx, var_1C
  loc_0041C391: call [004011F0h] ; __vbaFreeObj
  loc_0041C397: ret
  loc_0041C398: mov eax, Me
  loc_0041C39B: push eax
  loc_0041C39C: mov edx, [eax]
  loc_0041C39E: call [edx+00000008h]
  loc_0041C3A1: mov eax, arg_10
  loc_0041C3A4: mov ecx, var_2C
  loc_0041C3A7: mov edx, var_28
  loc_0041C3AA: mov [eax], ecx
  loc_0041C3AC: mov ecx, var_24
  loc_0041C3AF: mov [eax+00000004h], edx
  loc_0041C3B2: mov edx, var_20
  loc_0041C3B5: mov [eax+00000008h], ecx
  loc_0041C3B8: mov [eax+0000000Ch], edx
  loc_0041C3BB: mov eax, var_4
  loc_0041C3BE: mov ecx, var_14
  loc_0041C3C1: pop edi
  loc_0041C3C2: pop esi
  loc_0041C3C3: mov fs:[00000000h], ecx
  loc_0041C3CA: pop ebx
  loc_0041C3CB: mov esp, ebp
  loc_0041C3CD: pop ebp
  loc_0041C3CE: retn 000Ch
End Function

Private Sub Proc_1_15_419060(arg_C) '419060
  loc_00419060: push ebp
  loc_00419061: mov ebp, esp
  loc_00419063: sub esp, 0000000Ch
  loc_00419066: push 00401AA6h ; __vbaExceptHandler
  loc_0041906B: mov eax, fs:[00000000h]
  loc_00419071: push eax
  loc_00419072: mov fs:[00000000h], esp
  loc_00419079: sub esp, 00000174h
  loc_0041907F: push ebx
  loc_00419080: push esi
  loc_00419081: push edi
  loc_00419082: mov var_C, esp
  loc_00419085: mov var_8, 004015E8h
  loc_0041908C: mov eax, arg_C
  loc_0041908F: xor esi, esi
  loc_00419091: push 0040714Ch
  loc_00419096: mov var_18, esi
  loc_00419099: mov var_1C, esi
  loc_0041909C: mov var_2C, esi
  loc_0041909F: mov var_30, esi
  loc_004190A2: mov var_34, esi
  loc_004190A5: mov var_38, esi
  loc_004190A8: mov var_3C, esi
  loc_004190AB: mov var_40, esi
  loc_004190AE: mov var_50, esi
  loc_004190B1: mov var_60, esi
  loc_004190B4: mov var_70, esi
  loc_004190B7: mov var_80, esi
  loc_004190BA: mov var_90, esi
  loc_004190C0: mov var_A0, esi
  loc_004190C6: mov var_B0, esi
  loc_004190CC: mov var_C0, esi
  loc_004190D2: mov var_D0, esi
  loc_004190D8: mov var_E0, esi
  loc_004190DE: mov var_F0, esi
  loc_004190E4: mov var_100, esi
  loc_004190EA: mov var_120, esi
  loc_004190F0: mov var_130, esi
  loc_004190F6: mov var_154, esi
  loc_004190FC: mov [eax], esi
  loc_004190FE: call [00401110h] ; __vbaNew
  loc_00419104: lea ecx, var_30
  loc_00419107: push eax
  loc_00419108: push ecx
  loc_00419109: call [00401080h] ; __vbaObjSet
  loc_0041910F: mov edx, 00407450h ; "SELECT * FROM tblInstruments WHERE tblInstruments.fldIsLampElectrical = true"
  loc_00419114: lea ecx, var_1C
  loc_00419117: call [00401178h] ; __vbaStrCopy
  loc_0041911D: push FFFFFFFFh
  loc_0041911F: push FFFFFFFFh
  loc_00419121: push FFFFFFFFh
  loc_00419123: mov eax, [00423028h]
  loc_00419128: sub esp, 00000010h
  loc_0041912B: mov ecx, 00000009h
  loc_00419130: mov ebx, esp
  loc_00419132: mov var_F0, ecx
  loc_00419138: mov var_E8, eax
  loc_0041913E: sub esp, 00000010h
  loc_00419141: mov [ebx], ecx
  loc_00419143: mov ecx, var_EC
  loc_00419149: mov edx, var_1C
  loc_0041914C: mov edi, var_30
  loc_0041914F: mov [ebx+00000004h], ecx
  loc_00419152: mov var_E0, 00000008h
  loc_0041915C: mov ecx, esp
  loc_0041915E: mov var_D8, edx
  loc_00419164: mov [ebx+00000008h], eax
  loc_00419167: mov eax, var_E4
  loc_0041916D: mov edi, [edi]
  loc_0041916F: mov [ebx+0000000Ch], eax
  loc_00419172: mov eax, var_E0
  loc_00419178: mov [ecx], eax
  loc_0041917A: mov eax, var_DC
  loc_00419180: mov [ecx+00000004h], eax
  loc_00419183: mov eax, var_30
  loc_00419186: push eax
  loc_00419187: mov [ecx+00000008h], edx
  loc_0041918A: mov edx, var_D4
  loc_00419190: mov [ecx+0000000Ch], edx
  loc_00419193: call [edi+000000A0h]
  loc_00419199: cmp eax, esi
  loc_0041919B: fnclex
  loc_0041919D: jge 004191B8h
  loc_0041919F: mov ecx, var_30
  loc_004191A2: mov edi, [0040105Ch] ; __vbaHresultCheckObj
  loc_004191A8: push 000000A0h
  loc_004191AD: push 004072E8h
  loc_004191B2: push ecx
  loc_004191B3: push eax
  loc_004191B4: call edi
  loc_004191B6: jmp 004191BEh
  loc_004191B8: mov edi, [0040105Ch] ; __vbaHresultCheckObj
  loc_004191BE: mov eax, var_30
  loc_004191C1: lea ecx, var_34
  loc_004191C4: mov var_E8, 004074F0h ; "HPIB_"
  loc_004191CE: mov var_F0, 00000008h
  loc_004191D8: mov edx, [eax]
  loc_004191DA: push ecx
  loc_004191DB: push eax
  loc_004191DC: call [edx+00000054h]
  loc_004191DF: cmp eax, esi
  loc_004191E1: fnclex
  loc_004191E3: jge 004191F3h
  loc_004191E5: mov edx, var_30
  loc_004191E8: push 00000054h
  loc_004191EA: push 004072E8h
  loc_004191EF: push edx
  loc_004191F0: push eax
  loc_004191F1: call edi
  loc_004191F3: lea ebx, var_38
  loc_004191F6: mov eax, var_34
  loc_004191F9: push ebx
  loc_004191FA: mov edx, 00000008h
  loc_004191FF: sub esp, 00000010h
  loc_00419202: mov var_E0, edx
  loc_00419208: mov ebx, esp
  loc_0041920A: mov ecx, 00407500h ; "fldName"
  loc_0041920F: mov var_D8, ecx
  loc_00419215: mov edi, [eax]
  loc_00419217: mov [ebx], edx
  loc_00419219: mov edx, var_DC
  loc_0041921F: push eax
  loc_00419220: mov var_160, eax
  loc_00419226: mov [ebx+00000004h], edx
  loc_00419229: mov [ebx+00000008h], ecx
  loc_0041922C: mov ecx, var_D4
  loc_00419232: mov [ebx+0000000Ch], ecx
  loc_00419235: call [edi+00000028h]
  loc_00419238: cmp eax, esi
  loc_0041923A: fnclex
  loc_0041923C: jge 00419257h
  loc_0041923E: mov edx, var_160
  loc_00419244: mov ebx, [0040105Ch] ; __vbaHresultCheckObj
  loc_0041924A: push 00000028h
  loc_0041924C: push 00407390h
  loc_00419251: push edx
  loc_00419252: push eax
  loc_00419253: call ebx
  loc_00419255: jmp 0041925Dh
  loc_00419257: mov ebx, [0040105Ch] ; __vbaHresultCheckObj
  loc_0041925D: mov eax, var_38
  loc_00419260: lea edx, var_50
  loc_00419263: push edx
  loc_00419264: push eax
  loc_00419265: mov ecx, [eax]
  loc_00419267: mov edi, eax
  loc_00419269: call [ecx+00000034h]
  loc_0041926C: cmp eax, esi
  loc_0041926E: fnclex
  loc_00419270: jge 0041927Dh
  loc_00419272: push 00000034h
  loc_00419274: push 004073A0h
  loc_00419279: push edi
  loc_0041927A: push eax
  loc_0041927B: call ebx
  loc_0041927D: mov edi, Me
  loc_00419280: lea ecx, var_3C
  loc_00419283: push ecx
  loc_00419284: push edi
  loc_00419285: mov eax, [edi]
  loc_00419287: call [eax+00000218h]
  loc_0041928D: cmp eax, esi
  loc_0041928F: fnclex
  loc_00419291: jge 004192A1h
  loc_00419293: push 00000218h
  loc_00419298: push 0040576Ch
  loc_0041929D: push edi
  loc_0041929E: push eax
  loc_0041929F: call ebx
  loc_004192A1: lea edx, var_F0
  loc_004192A7: push 00405B4Ch
  loc_004192AC: lea eax, var_50
  loc_004192AF: push edx
  loc_004192B0: lea ecx, var_60
  loc_004192B3: push eax
  loc_004192B4: push ecx
  loc_004192B5: call [004011ACh] ; __vbaVarAdd
  loc_004192BB: mov ecx, [eax]
  loc_004192BD: sub esp, 00000010h
  loc_004192C0: mov edx, esp
  loc_004192C2: push 00000001h
  loc_004192C4: push esi
  loc_004192C5: mov [edx], ecx
  loc_004192C7: mov ecx, [eax+00000004h]
  loc_004192CA: mov [edx+00000004h], ecx
  loc_004192CD: mov ecx, [eax+00000008h]
  loc_004192D0: mov eax, [eax+0000000Ch]
  loc_004192D3: mov [edx+00000008h], ecx
  loc_004192D6: mov ecx, var_3C
  loc_004192D9: mov [edx+0000000Ch], eax
  loc_004192DC: lea edx, var_70
  loc_004192DF: push ecx
  loc_004192E0: push edx
  loc_004192E1: call [00401100h] ; __vbaLateIdCallLd
  loc_004192E7: add esp, 00000020h
  loc_004192EA: push eax
  loc_004192EB: call [004010F4h] ; __vbaCastObjVar
  loc_004192F1: push eax
  loc_004192F2: lea eax, var_18
  loc_004192F5: push eax
  loc_004192F6: call [00401080h] ; __vbaObjSet
  loc_004192FC: lea ecx, var_3C
  loc_004192FF: lea edx, var_38
  loc_00419302: push ecx
  loc_00419303: lea eax, var_34
  loc_00419306: push edx
  loc_00419307: push eax
  loc_00419308: push 00000003h
  loc_0041930A: call [00401040h] ; __vbaFreeObjList
  loc_00419310: lea ecx, var_70
  loc_00419313: lea edx, var_60
  loc_00419316: push ecx
  loc_00419317: lea eax, var_50
  loc_0041931A: push edx
  loc_0041931B: push eax
  loc_0041931C: push 00000003h
  loc_0041931E: call [00401038h] ; __vbaFreeVarList
  loc_00419324: mov eax, var_30
  loc_00419327: add esp, 00000020h
  loc_0041932A: lea edx, var_34
  loc_0041932D: mov ecx, [eax]
  loc_0041932F: push edx
  loc_00419330: push eax
  loc_00419331: call [ecx+00000054h]
  loc_00419334: cmp eax, esi
  loc_00419336: fnclex
  loc_00419338: jge 00419348h
  loc_0041933A: mov ecx, var_30
  loc_0041933D: push 00000054h
  loc_0041933F: push 004072E8h
  loc_00419344: push ecx
  loc_00419345: push eax
  loc_00419346: call ebx
  loc_00419348: lea ebx, var_38
  loc_0041934B: mov eax, var_34
  loc_0041934E: push ebx
  loc_0041934F: mov edx, 00000008h
  loc_00419354: sub esp, 00000010h
  loc_00419357: mov var_E0, edx
  loc_0041935D: mov ebx, esp
  loc_0041935F: mov ecx, 00407514h ; "fldAddress"
  loc_00419364: mov var_D8, ecx
  loc_0041936A: mov edi, [eax]
  loc_0041936C: mov [ebx], edx
  loc_0041936E: mov edx, var_DC
  loc_00419374: push eax
  loc_00419375: mov var_15C, eax
  loc_0041937B: mov [ebx+00000004h], edx
  loc_0041937E: mov [ebx+00000008h], ecx
  loc_00419381: mov ecx, var_D4
  loc_00419387: mov [ebx+0000000Ch], ecx
  loc_0041938A: call [edi+00000028h]
  loc_0041938D: cmp eax, esi
  loc_0041938F: fnclex
  loc_00419391: jge 004193ACh
  loc_00419393: mov edx, var_15C
  loc_00419399: mov edi, [0040105Ch] ; __vbaHresultCheckObj
  loc_0041939F: push 00000028h
  loc_004193A1: push 00407390h
  loc_004193A6: push edx
  loc_004193A7: push eax
  loc_004193A8: call edi
  loc_004193AA: jmp 004193B2h
  loc_004193AC: mov edi, [0040105Ch] ; __vbaHresultCheckObj
  loc_004193B2: sub esp, 00000010h
  loc_004193B5: mov eax, var_38
  loc_004193B8: mov edx, esp
  loc_004193BA: mov ecx, 00000009h
  loc_004193BF: mov var_50, ecx
  loc_004193C2: mov var_48, eax
  loc_004193C5: mov [edx], ecx
  loc_004193C7: mov ecx, var_4C
  loc_004193CA: push 0040752Ch ; "Address"
  loc_004193CF: mov var_38, esi
  loc_004193D2: mov [edx+00000004h], ecx
  loc_004193D5: mov ecx, var_18
  loc_004193D8: push ecx
  loc_004193D9: mov [edx+00000008h], eax
  loc_004193DC: mov eax, var_44
  loc_004193DF: mov [edx+0000000Ch], eax
  loc_004193E2: call [00401068h] ; __vbaLateMemSt
  loc_004193E8: lea ecx, var_34
  loc_004193EB: call [004011F0h] ; __vbaFreeObj
  loc_004193F1: lea ecx, var_50
  loc_004193F4: call [00401020h] ; __vbaFreeVar
  loc_004193FA: mov eax, var_30
  loc_004193FD: push eax
  loc_004193FE: mov edx, [eax]
  loc_00419400: call [edx+00000090h]
  loc_00419406: cmp eax, esi
  loc_00419408: fnclex
  loc_0041940A: jge 0041941Dh
  loc_0041940C: mov ecx, var_30
  loc_0041940F: push 00000090h
  loc_00419414: push 004072E8h
  loc_00419419: push ecx
  loc_0041941A: push eax
  loc_0041941B: call edi
  loc_0041941D: mov eax, var_30
  loc_00419420: lea ecx, var_154
  loc_00419426: push ecx
  loc_00419427: push eax
  loc_00419428: mov edx, [eax]
  loc_0041942A: call [edx+00000050h]
  loc_0041942D: cmp eax, esi
  loc_0041942F: fnclex
  loc_00419431: jge 00419441h
  loc_00419433: mov edx, var_30
  loc_00419436: push 00000050h
  loc_00419438: push 004072E8h
  loc_0041943D: push edx
  loc_0041943E: push eax
  loc_0041943F: call edi
  loc_00419441: cmp var_154, si
  loc_00419448: jz 004191BEh
  loc_0041944E: lea edx, var_E0
  loc_00419454: lea ecx, var_2C
  loc_00419457: mov var_D8, esi
  loc_0041945D: mov var_E0, 00000002h
  loc_00419467: call [00401014h] ; __vbaVarMove
  loc_0041946D: mov eax, var_30
  loc_00419470: push eax
  loc_00419471: mov ecx, [eax]
  loc_00419473: call [ecx+00000080h]
  loc_00419479: cmp eax, esi
  loc_0041947B: fnclex
  loc_0041947D: jge 00419490h
  loc_0041947F: mov edx, var_30
  loc_00419482: push 00000080h
  loc_00419487: push 004072E8h
  loc_0041948C: push edx
  loc_0041948D: push eax
  loc_0041948E: call edi
  loc_00419490: push 0040713Ch
  loc_00419495: push esi
  loc_00419496: call [004011D4h] ; __vbaCastObj
  loc_0041949C: push eax
  loc_0041949D: lea eax, var_30
  loc_004194A0: push eax
  loc_004194A1: call [00401080h] ; __vbaObjSet
  loc_004194A7: push 0041952Eh
  loc_004194AC: jmp 00419514h
  loc_004194AE: test var_4, 04h
  loc_004194B2: jz 004194BDh
  loc_004194B4: lea ecx, var_2C
  loc_004194B7: call [00401020h] ; __vbaFreeVar
  loc_004194BD: lea ecx, var_40
  loc_004194C0: lea edx, var_3C
  loc_004194C3: push ecx
  loc_004194C4: lea eax, var_38
  loc_004194C7: push edx
  loc_004194C8: lea ecx, var_34
  loc_004194CB: push eax
  loc_004194CC: push ecx
  loc_004194CD: push 00000004h
  loc_004194CF: call [00401040h] ; __vbaFreeObjList
  loc_004194D5: lea edx, var_D0
  loc_004194DB: lea eax, var_C0
  loc_004194E1: push edx
  loc_004194E2: lea ecx, var_B0
  loc_004194E8: push eax
  loc_004194E9: lea edx, var_A0
  loc_004194EF: push ecx
  loc_004194F0: lea eax, var_90
  loc_004194F6: push edx
  loc_004194F7: lea ecx, var_80
  loc_004194FA: push eax
  loc_004194FB: lea edx, var_70
  loc_004194FE: push ecx
  loc_004194FF: lea eax, var_60
  loc_00419502: push edx
  loc_00419503: lea ecx, var_50
  loc_00419506: push eax
  loc_00419507: push ecx
  loc_00419508: push 00000009h
  loc_0041950A: call [00401038h] ; __vbaFreeVarList
  loc_00419510: add esp, 0000003Ch
  loc_00419513: ret
  loc_00419514: mov esi, [004011F0h] ; __vbaFreeObj
  loc_0041951A: lea ecx, var_18
  loc_0041951D: call __vbaFreeObj
  loc_0041951F: lea ecx, var_1C
  loc_00419522: call [004011F4h] ; __vbaFreeStr
  loc_00419528: lea ecx, var_30
  loc_0041952B: call __vbaFreeObj
  loc_0041952D: ret
  loc_0041952E: mov edx, arg_C
  loc_00419531: mov eax, var_2C
  loc_00419534: mov ecx, var_28
  loc_00419537: pop edi
  loc_00419538: mov [edx], eax
  loc_0041953A: mov eax, var_24
  loc_0041953D: pop esi
  loc_0041953E: pop ebx
  loc_0041953F: mov [edx+00000004h], ecx
  loc_00419542: mov ecx, var_20
  loc_00419545: mov [edx+00000008h], eax
  loc_00419548: xor eax, eax
  loc_0041954A: mov [edx+0000000Ch], ecx
  loc_0041954D: mov ecx, var_14
  loc_00419550: mov fs:[00000000h], ecx
  loc_00419557: mov esp, ebp
  loc_00419559: pop ebp
  loc_0041955A: retn 0008h
End Sub

Private Sub Proc_1_16_419560(arg_C, arg_10) '419560
  loc_00419560: push ebp
  loc_00419561: mov ebp, esp
  loc_00419563: sub esp, 0000000Ch
  loc_00419566: push 00401AA6h ; __vbaExceptHandler
  loc_0041956B: mov eax, fs:[00000000h]
  loc_00419571: push eax
  loc_00419572: mov fs:[00000000h], esp
  loc_00419579: sub esp, 00000080h
  loc_0041957F: push ebx
  loc_00419580: push esi
  loc_00419581: push edi
  loc_00419582: mov var_C, esp
  loc_00419585: mov var_8, 004015F8h
  loc_0041958C: mov ecx, arg_10
  loc_0041958F: mov ebx, arg_C
  loc_00419592: mov esi, [0040102Ch] ; __vbaLenBstr
  loc_00419598: xor eax, eax
  loc_0041959A: mov [ecx], eax
  loc_0041959C: mov edx, [ebx]
  loc_0041959E: push edx
  loc_0041959F: mov var_1C, eax
  loc_004195A2: mov var_20, eax
  loc_004195A5: mov var_30, eax
  loc_004195A8: mov var_40, eax
  loc_004195AB: mov var_50, eax
  loc_004195AE: mov var_60, eax
  loc_004195B1: mov var_80, eax
  loc_004195B4: call __vbaLenBstr
  loc_004195B6: test eax, eax
  loc_004195B8: jnz 004195CFh
  loc_004195BA: xor edx, edx
  loc_004195BC: lea ecx, var_1C
  loc_004195BF: call [00401178h] ; __vbaStrCopy
  loc_004195C5: push 0041974Ch
  loc_004195CA: jmp 00419742h
  loc_004195CF: xor edx, edx
  loc_004195D1: lea ecx, var_20
  loc_004195D4: call [00401178h] ; __vbaStrCopy
  loc_004195DA: mov eax, [ebx]
  loc_004195DC: push eax
  loc_004195DD: call __vbaLenBstr
  loc_004195DF: mov ecx, eax
  loc_004195E1: call [004010ECh] ; __vbaI2I4
  loc_004195E7: mov var_8C, eax
  loc_004195ED: mov eax, 00000001h
  loc_004195F2: mov var_18, eax
  loc_004195F5: cmp ax, var_8C
  loc_004195FC: jg 00419708h
  loc_00419602: movsx esi, ax
  loc_00419605: lea ecx, var_30
  loc_00419608: lea edx, var_60
  loc_0041960B: push ecx
  loc_0041960C: push esi
  loc_0041960D: lea eax, var_40
  loc_00419610: push edx
  loc_00419611: push eax
  loc_00419612: mov var_28, 00000001h
  loc_00419619: mov var_30, 00000002h
  loc_00419620: mov var_58, ebx
  loc_00419623: mov var_60, 00004008h
  loc_0041962A: call [004010BCh] ; rtcMidCharVar
  loc_00419630: lea ecx, var_40
  loc_00419633: lea edx, var_80
  loc_00419636: push ecx
  loc_00419637: push edx
  loc_00419638: mov var_78, 00407594h ; ":"
  loc_0041963F: mov var_80, 00008008h
  loc_00419646: call [00401198h] ; __vbaVarTstNe
  loc_0041964C: mov edi, eax
  loc_0041964E: lea eax, var_40
  loc_00419651: lea ecx, var_30
  loc_00419654: push eax
  loc_00419655: push ecx
  loc_00419656: push 00000002h
  loc_00419658: call [00401038h] ; __vbaFreeVarList
  loc_0041965E: add esp, 0000000Ch
  loc_00419661: test di, di
  loc_00419664: jz 004196DBh
  loc_00419666: mov edx, var_20
  loc_00419669: lea eax, var_30
  loc_0041966C: mov var_78, edx
  loc_0041966F: push eax
  loc_00419670: lea ecx, var_60
  loc_00419673: push esi
  loc_00419674: lea edx, var_40
  loc_00419677: push ecx
  loc_00419678: push edx
  loc_00419679: mov var_80, 00000008h
  loc_00419680: mov var_28, 00000001h
  loc_00419687: mov var_30, 00000002h
  loc_0041968E: mov var_58, ebx
  loc_00419691: mov var_60, 00004008h
  loc_00419698: call [004010BCh] ; rtcMidCharVar
  loc_0041969E: lea eax, var_80
  loc_004196A1: lea ecx, var_40
  loc_004196A4: push eax
  loc_004196A5: lea edx, var_50
  loc_004196A8: push ecx
  loc_004196A9: push edx
  loc_004196AA: call [004011ACh] ; __vbaVarAdd
  loc_004196B0: push eax
  loc_004196B1: call [00401030h] ; __vbaStrVarMove
  loc_004196B7: mov edx, eax
  loc_004196B9: lea ecx, var_20
  loc_004196BC: call [004011D0h] ; __vbaStrMove
  loc_004196C2: lea eax, var_50
  loc_004196C5: lea ecx, var_40
  loc_004196C8: push eax
  loc_004196C9: lea edx, var_30
  loc_004196CC: push ecx
  loc_004196CD: push edx
  loc_004196CE: push 00000003h
  loc_004196D0: call [00401038h] ; __vbaFreeVarList
  loc_004196D6: add esp, 00000010h
  loc_004196D9: jmp 004196F5h
  loc_004196DB: mov eax, var_20
  loc_004196DE: push eax
  loc_004196DF: push 00407448h
  loc_004196E4: call [00401050h] ; __vbaStrCat
  loc_004196EA: mov edx, eax
  loc_004196EC: lea ecx, var_20
  loc_004196EF: call [004011D0h] ; __vbaStrMove
  loc_004196F5: mov eax, 00000001h
  loc_004196FA: add ax, var_18
  loc_004196FE: jo 00419769h
  loc_00419700: mov var_18, eax
  loc_00419703: jmp 004195F5h
  loc_00419708: mov edx, var_20
  loc_0041970B: lea ecx, var_1C
  loc_0041970E: call [00401178h] ; __vbaStrCopy
  loc_00419714: push 0041974Ch
  loc_00419719: jmp 00419742h
  loc_0041971B: test var_4, 04h
  loc_0041971F: jz 0041972Ah
  loc_00419721: lea ecx, var_1C
  loc_00419724: call [004011F4h] ; __vbaFreeStr
  loc_0041972A: lea ecx, var_50
  loc_0041972D: lea edx, var_40
  loc_00419730: push ecx
  loc_00419731: lea eax, var_30
  loc_00419734: push edx
  loc_00419735: push eax
  loc_00419736: push 00000003h
  loc_00419738: call [00401038h] ; __vbaFreeVarList
  loc_0041973E: add esp, 00000010h
  loc_00419741: ret
  loc_00419742: lea ecx, var_20
  loc_00419745: call [004011F4h] ; __vbaFreeStr
  loc_0041974B: ret
  loc_0041974C: mov ecx, arg_10
  loc_0041974F: mov edx, var_1C
  loc_00419752: pop edi
  loc_00419753: pop esi
  loc_00419754: mov [ecx], edx
  loc_00419756: mov ecx, var_14
  loc_00419759: xor eax, eax
  loc_0041975B: mov fs:[00000000h], ecx
  loc_00419762: pop ebx
  loc_00419763: mov esp, ebp
  loc_00419765: pop ebp
  loc_00419766: retn 000Ch
End Sub

Private Sub Proc_1_17_419A90(arg_C, arg_10) '419A90
  loc_00419A90: push ebp
  loc_00419A91: mov ebp, esp
  loc_00419A93: sub esp, 00000014h
  loc_00419A96: push 00401AA6h ; __vbaExceptHandler
  loc_00419A9B: mov eax, fs:[00000000h]
  loc_00419AA1: push eax
  loc_00419AA2: mov fs:[00000000h], esp
  loc_00419AA9: sub esp, 0000008Ch
  loc_00419AAF: push ebx
  loc_00419AB0: push esi
  loc_00419AB1: push edi
  loc_00419AB2: mov var_14, esp
  loc_00419AB5: mov var_10, 00401618h
  loc_00419ABC: xor ebx, ebx
  loc_00419ABE: mov var_C, ebx
  loc_00419AC1: mov var_8, ebx
  loc_00419AC4: mov var_20, ebx
  loc_00419AC7: mov var_30, ebx
  loc_00419ACA: mov var_38, ebx
  loc_00419ACD: mov var_3C, ebx
  loc_00419AD0: mov var_40, ebx
  loc_00419AD3: mov var_50, ebx
  loc_00419AD6: mov var_60, ebx
  loc_00419AD9: mov var_70, ebx
  loc_00419ADC: mov var_80, ebx
  loc_00419ADF: mov var_84, ebx
  loc_00419AE5: mov eax, arg_10
  loc_00419AE8: mov [eax], ebx
  loc_00419AEA: mov esi, Me
  loc_00419AED: mov ecx, [esi]
  loc_00419AEF: push esi
  loc_00419AF0: call [ecx+00000380h]
  loc_00419AF6: push eax
  loc_00419AF7: lea edx, var_40
  loc_00419AFA: push edx
  loc_00419AFB: call [00401080h] ; __vbaObjSet
  loc_00419B01: mov edi, eax
  loc_00419B03: mov eax, [edi]
  loc_00419B05: lea ecx, var_84
  loc_00419B0B: push ecx
  loc_00419B0C: push edi
  loc_00419B0D: call [eax+000000E0h]
  loc_00419B13: fnclex
  loc_00419B15: cmp eax, ebx
  loc_00419B17: jge 00419B2Bh
  loc_00419B19: push 000000E0h
  loc_00419B1E: push 00405354h
  loc_00419B23: push edi
  loc_00419B24: push eax
  loc_00419B25: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00419B2B: xor edx, edx
  loc_00419B2D: cmp var_84, 0001h
  loc_00419B35: setnz dl
  loc_00419B38: neg edx
  loc_00419B3A: mov edi, edx
  loc_00419B3C: lea ecx, var_40
  loc_00419B3F: call [004011F0h] ; __vbaFreeObj
  loc_00419B45: cmp di, bx
  loc_00419B48: jnz 00419C9Ch
  loc_00419B4E: mov edi, [004011D0h] ; __vbaStrMove
  loc_00419B54: push 00000001h
  loc_00419B56: call [0040107Ch] ; __vbaOnError
  loc_00419B5C: mov eax, [esi]
  loc_00419B5E: push esi
  loc_00419B5F: call [eax+0000037Ch]
  loc_00419B65: mov var_48, eax
  loc_00419B68: mov var_50, 00000009h
  loc_00419B6F: push ebx
  loc_00419B70: lea ecx, var_50
  loc_00419B73: push ecx
  loc_00419B74: call [00401150h] ; rtcDir
  loc_00419B7A: mov edx, eax
  loc_00419B7C: lea ecx, var_20
  loc_00419B7F: call edi
  loc_00419B81: lea ecx, var_50
  loc_00419B84: mov edi, [00401020h] ; __vbaFreeVar
  loc_00419B8A: call edi
  loc_00419B8C: mov var_48, 80020004h
  loc_00419B93: mov var_50, 0000000Ah
  loc_00419B9A: lea edx, var_50
  loc_00419B9D: push edx
  loc_00419B9E: call [00401164h] ; rtcFreeFile
  loc_00419BA4: movsx ebx, ax
  loc_00419BA7: lea ecx, var_50
  loc_00419BAA: call edi
  loc_00419BAC: mov eax, var_20
  loc_00419BAF: push eax
  loc_00419BB0: push 00000000h
  loc_00419BB2: call [004010DCh] ; __vbaStrCmp
  loc_00419BB8: test eax, eax
  loc_00419BBA: jnz 00419C0Ch
  loc_00419BBC: mov ecx, [esi]
  loc_00419BBE: push esi
  loc_00419BBF: call [ecx+0000037Ch]
  loc_00419BC5: push eax
  loc_00419BC6: lea edx, var_40
  loc_00419BC9: push edx
  loc_00419BCA: call [00401080h] ; __vbaObjSet
  loc_00419BD0: mov esi, eax
  loc_00419BD2: mov eax, [esi]
  loc_00419BD4: lea ecx, var_38
  loc_00419BD7: push ecx
  loc_00419BD8: push esi
  loc_00419BD9: call [eax+000000A0h]
  loc_00419BDF: fnclex
  loc_00419BE1: test eax, eax
  loc_00419BE3: jge 00419BF7h
  loc_00419BE5: push 000000A0h
  loc_00419BEA: push 00405398h
  loc_00419BEF: push esi
  loc_00419BF0: push eax
  loc_00419BF1: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00419BF7: mov edx, var_38
  loc_00419BFA: push edx
  loc_00419BFB: mov ecx, ebx
  loc_00419BFD: mov esi, [004010ECh] ; __vbaI2I4
  loc_00419C03: call __vbaI2I4
  loc_00419C05: push eax
  loc_00419C06: push FFFFFFFFh
  loc_00419C08: push 00000002h
  loc_00419C0A: jmp 00419C5Ah
  loc_00419C0C: mov eax, [esi]
  loc_00419C0E: push esi
  loc_00419C0F: call [eax+0000037Ch]
  loc_00419C15: push eax
  loc_00419C16: lea ecx, var_40
  loc_00419C19: push ecx
  loc_00419C1A: call [00401080h] ; __vbaObjSet
  loc_00419C20: mov esi, eax
  loc_00419C22: mov edx, [esi]
  loc_00419C24: lea eax, var_38
  loc_00419C27: push eax
  loc_00419C28: push esi
  loc_00419C29: call [edx+000000A0h]
  loc_00419C2F: fnclex
  loc_00419C31: test eax, eax
  loc_00419C33: jge 00419C47h
  loc_00419C35: push 000000A0h
  loc_00419C3A: push 00405398h
  loc_00419C3F: push esi
  loc_00419C40: push eax
  loc_00419C41: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00419C47: mov ecx, var_38
  loc_00419C4A: push ecx
  loc_00419C4B: mov ecx, ebx
  loc_00419C4D: mov esi, [004010ECh] ; __vbaI2I4
  loc_00419C53: call __vbaI2I4
  loc_00419C55: push eax
  loc_00419C56: push FFFFFFFFh
  loc_00419C58: push 00000008h
  loc_00419C5A: call [0040115Ch] ; __vbaFileOpen
  loc_00419C60: lea ecx, var_38
  loc_00419C63: call [004011F4h] ; __vbaFreeStr
  loc_00419C69: lea ecx, var_40
  loc_00419C6C: call [004011F0h] ; __vbaFreeObj
  loc_00419C72: mov edx, arg_C
  loc_00419C75: mov eax, [edx]
  loc_00419C77: push eax
  loc_00419C78: mov ecx, ebx
  loc_00419C7A: call __vbaI2I4
  loc_00419C7C: push eax
  loc_00419C7D: push 0040759Ch
  loc_00419C82: call [00401128h] ; __vbaPrintFile
  loc_00419C88: add esp, 0000000Ch
  loc_00419C8B: mov ecx, ebx
  loc_00419C8D: call __vbaI2I4
  loc_00419C8F: push eax
  loc_00419C90: call [004010CCh] ; __vbaFileClose
  loc_00419C96: call [004010A0h] ; rtcDoEvents
  loc_00419C9C: call [00401074h] ; __vbaExitProc
  loc_00419CA2: push 00419E40h
  loc_00419CA7: jmp 00419E36h
  loc_00419CAC: call [00401190h] ; rtcErrObj
  loc_00419CB2: push eax
  loc_00419CB3: lea ecx, var_40
  loc_00419CB6: push ecx
  loc_00419CB7: mov ebx, [00401080h] ; __vbaObjSet
  loc_00419CBD: call ebx
  loc_00419CBF: mov edx, [eax]
  loc_00419CC1: push eax
  loc_00419CC2: call [edx+00000048h]
  loc_00419CC5: lea ecx, var_40
  loc_00419CC8: call [004011F0h] ; __vbaFreeObj
  loc_00419CCE: lea eax, var_50
  loc_00419CD1: push eax
  loc_00419CD2: call [004011E4h] ; rtcGetPresentDate
  loc_00419CD8: mov var_78, 00407234h ; "mm dd yyyy hh:mm:ss AMPM"
  loc_00419CDF: mov var_80, 00000008h
  loc_00419CE6: lea edx, var_80
  loc_00419CE9: lea ecx, var_60
  loc_00419CEC: call [004011B4h] ; __vbaVarDup
  loc_00419CF2: push 00000001h
  loc_00419CF4: push 00000001h
  loc_00419CF6: lea ecx, var_60
  loc_00419CF9: push ecx
  loc_00419CFA: lea edx, var_50
  loc_00419CFD: push edx
  loc_00419CFE: lea eax, var_70
  loc_00419D01: push eax
  loc_00419D02: call [00401054h] ; rtcVarFromFormatVar
  loc_00419D08: lea ecx, var_70
  loc_00419D0B: push ecx
  loc_00419D0C: call [00401030h] ; __vbaStrVarMove
  loc_00419D12: mov edx, eax
  loc_00419D14: lea ecx, var_20
  loc_00419D17: mov edi, [004011D0h] ; __vbaStrMove
  loc_00419D1D: call edi
  loc_00419D1F: lea edx, var_70
  loc_00419D22: push edx
  loc_00419D23: lea eax, var_60
  loc_00419D26: push eax
  loc_00419D27: lea ecx, var_50
  loc_00419D2A: push ecx
  loc_00419D2B: push 00000003h
  loc_00419D2D: call [00401038h] ; __vbaFreeVarList
  loc_00419D33: add esp, 00000010h
  loc_00419D36: mov esi, Me
  loc_00419D39: mov edx, [esi]
  loc_00419D3B: lea eax, var_38
  loc_00419D3E: push eax
  loc_00419D3F: lea ecx, var_20
  loc_00419D42: push ecx
  loc_00419D43: push esi
  loc_00419D44: call [edx+00000728h]
  loc_00419D4A: mov edx, var_38
  loc_00419D4D: mov var_38, 00000000h
  loc_00419D54: lea ecx, var_20
  loc_00419D57: call edi
  loc_00419D59: mov edx, [esi]
  loc_00419D5B: push esi
  loc_00419D5C: call [edx+0000037Ch]
  loc_00419D62: push eax
  loc_00419D63: lea eax, var_40
  loc_00419D66: push eax
  loc_00419D67: call ebx
  loc_00419D69: mov var_88, eax
  loc_00419D6F: mov ebx, [eax]
  loc_00419D71: push 00405E08h ; "C:\ProbeData\"
  loc_00419D76: mov ecx, var_20
  loc_00419D79: push ecx
  loc_00419D7A: call [00401050h] ; __vbaStrCat
  loc_00419D80: mov edx, eax
  loc_00419D82: lea ecx, var_38
  loc_00419D85: call edi
  loc_00419D87: push eax
  loc_00419D88: push 0040726Ch ; ".txt"
  loc_00419D8D: call [00401050h] ; __vbaStrCat
  loc_00419D93: mov edx, eax
  loc_00419D95: lea ecx, var_3C
  loc_00419D98: call edi
  loc_00419D9A: push eax
  loc_00419D9B: mov edx, ebx
  loc_00419D9D: mov ebx, var_88
  loc_00419DA3: push ebx
  loc_00419DA4: call [edx+000000A4h]
  loc_00419DAA: fnclex
  loc_00419DAC: test eax, eax
  loc_00419DAE: jge 00419DC2h
  loc_00419DB0: push 000000A4h
  loc_00419DB5: push 00405398h
  loc_00419DBA: push ebx
  loc_00419DBB: push eax
  loc_00419DBC: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00419DC2: lea eax, var_3C
  loc_00419DC5: push eax
  loc_00419DC6: lea ecx, var_38
  loc_00419DC9: push ecx
  loc_00419DCA: push 00000002h
  loc_00419DCC: call [00401180h] ; __vbaFreeStrList
  loc_00419DD2: add esp, 0000000Ch
  loc_00419DD5: lea ecx, var_40
  loc_00419DD8: call [004011F0h] ; __vbaFreeObj
  loc_00419DDE: call [004010A0h] ; rtcDoEvents
  loc_00419DE4: push 00000000h
  loc_00419DE6: call [0040104Ch] ; __vbaResume
  loc_00419DEC: xor ebx, ebx
  loc_00419DEE: jmp 00419B54h
  loc_00419DF3: test var_C, 04h
  loc_00419DF7: jz 00419E02h
  loc_00419DF9: lea ecx, var_30
  loc_00419DFC: call [00401020h] ; __vbaFreeVar
  loc_00419E02: lea edx, var_3C
  loc_00419E05: push edx
  loc_00419E06: lea eax, var_38
  loc_00419E09: push eax
  loc_00419E0A: push 00000002h
  loc_00419E0C: call [00401180h] ; __vbaFreeStrList
  loc_00419E12: add esp, 0000000Ch
  loc_00419E15: lea ecx, var_40
  loc_00419E18: call [004011F0h] ; __vbaFreeObj
  loc_00419E1E: lea ecx, var_70
  loc_00419E21: push ecx
  loc_00419E22: lea edx, var_60
  loc_00419E25: push edx
  loc_00419E26: lea eax, var_50
  loc_00419E29: push eax
  loc_00419E2A: push 00000003h
  loc_00419E2C: call [00401038h] ; __vbaFreeVarList
  loc_00419E32: add esp, 00000010h
  loc_00419E35: ret
  loc_00419E36: lea ecx, var_20
  loc_00419E39: call [004011F4h] ; __vbaFreeStr
  loc_00419E3F: ret
  loc_00419E40: mov ecx, arg_10
  loc_00419E43: mov edx, var_30
  loc_00419E46: mov [ecx], edx
  loc_00419E48: mov eax, var_2C
  loc_00419E4B: mov [ecx+00000004h], eax
  loc_00419E4E: mov edx, var_28
  loc_00419E51: mov [ecx+00000008h], edx
  loc_00419E54: mov eax, var_24
  loc_00419E57: mov [ecx+0000000Ch], eax
  loc_00419E5A: xor eax, eax
  loc_00419E5C: mov ecx, var_1C
  loc_00419E5F: mov fs:[00000000h], ecx
  loc_00419E66: pop edi
  loc_00419E67: pop esi
  loc_00419E68: pop ebx
  loc_00419E69: mov esp, ebp
  loc_00419E6B: pop ebp
  loc_00419E6C: retn 000Ch
End Sub

Private Sub Proc_1_18_419E70(arg_C) '419E70
  loc_00419E70: push ebp
  loc_00419E71: mov ebp, esp
  loc_00419E73: sub esp, 00000008h
  loc_00419E76: push 00401AA6h ; __vbaExceptHandler
  loc_00419E7B: mov eax, fs:[00000000h]
  loc_00419E81: push eax
  loc_00419E82: mov fs:[00000000h], esp
  loc_00419E89: sub esp, 0000004Ch
  loc_00419E8C: push ebx
  loc_00419E8D: push esi
  loc_00419E8E: push edi
  loc_00419E8F: mov var_8, esp
  loc_00419E92: mov var_4, 00401640h
  loc_00419E99: mov eax, Me
  loc_00419E9C: xor edi, edi
  loc_00419E9E: push 00405B4Ch
  loc_00419EA3: push eax
  loc_00419EA4: mov ecx, [eax]
  loc_00419EA6: mov var_14, edi
  loc_00419EA9: mov var_18, edi
  loc_00419EAC: mov var_1C, edi
  loc_00419EAF: mov var_20, edi
  loc_00419EB2: call [ecx+00000324h]
  loc_00419EB8: mov esi, [00401080h] ; __vbaObjSet
  loc_00419EBE: lea edx, var_20
  loc_00419EC1: push eax
  loc_00419EC2: push edx
  loc_00419EC3: call __vbaObjSet
  loc_00419EC5: push eax
  loc_00419EC6: call [004011D4h] ; __vbaCastObj
  loc_00419ECC: push eax
  loc_00419ECD: lea eax, var_14
  loc_00419ED0: push eax
  loc_00419ED1: call __vbaObjSet
  loc_00419ED3: lea ecx, var_20
  loc_00419ED6: call [004011F0h] ; __vbaFreeObj
  loc_00419EDC: mov ecx, var_14
  loc_00419EDF: mov esi, [004011A8h] ; __vbaLateMemCall
  loc_00419EE5: push edi
  loc_00419EE6: push 004075A0h ; "Clear"
  loc_00419EEB: push ecx
  loc_00419EEC: call __vbaLateMemCall
  loc_00419EEE: mov ecx, 00000008h
  loc_00419EF3: mov edi, var_2C
  loc_00419EF6: push ecx
  loc_00419EF7: mov ebx, var_24
  loc_00419EFA: mov edx, esp
  loc_00419EFC: mov eax, 004075B0h
  loc_00419F01: push 00000001h
  loc_00419F03: push 004075B4h ; "AddItem"
  loc_00419F08: mov [edx], ecx
  loc_00419F0A: mov [edx+00000004h], edi
  loc_00419F0D: mov [edx+00000008h], eax
  loc_00419F10: mov eax, var_14
  loc_00419F13: push eax
  loc_00419F14: mov [edx+0000000Ch], ebx
  loc_00419F17: call __vbaLateMemCall
  loc_00419F19: add esp, 0000000Ch
  loc_00419F1C: mov ecx, 00000008h
  loc_00419F21: mov edx, esp
  loc_00419F23: mov eax, 004075C8h
  loc_00419F28: push 00000001h
  loc_00419F2A: push 004075B4h ; "AddItem"
  loc_00419F2F: mov [edx], ecx
  loc_00419F31: mov [edx+00000004h], edi
  loc_00419F34: mov [edx+00000008h], eax
  loc_00419F37: mov eax, var_14
  loc_00419F3A: push eax
  loc_00419F3B: mov [edx+0000000Ch], ebx
  loc_00419F3E: call __vbaLateMemCall
  loc_00419F40: add esp, 0000000Ch
  loc_00419F43: mov ecx, 00000008h
  loc_00419F48: mov edx, esp
  loc_00419F4A: mov eax, 004075D0h
  loc_00419F4F: push 00000001h
  loc_00419F51: push 004075B4h ; "AddItem"
  loc_00419F56: mov [edx], ecx
  loc_00419F58: mov [edx+00000004h], edi
  loc_00419F5B: mov [edx+00000008h], eax
  loc_00419F5E: mov eax, var_14
  loc_00419F61: push eax
  loc_00419F62: mov [edx+0000000Ch], ebx
  loc_00419F65: call __vbaLateMemCall
  loc_00419F67: add esp, 0000000Ch
  loc_00419F6A: mov ecx, 00000008h
  loc_00419F6F: mov edx, esp
  loc_00419F71: mov eax, 004075D8h
  loc_00419F76: mov [edx], ecx
  loc_00419F78: mov [edx+00000004h], edi
  loc_00419F7B: mov [edx+00000008h], eax
  loc_00419F7E: mov eax, var_14
  loc_00419F81: push 00000001h
  loc_00419F83: push 004075B4h ; "AddItem"
  loc_00419F88: push eax
  loc_00419F89: mov [edx+0000000Ch], ebx
  loc_00419F8C: call __vbaLateMemCall
  loc_00419F8E: add esp, 0000000Ch
  loc_00419F91: mov ecx, 00000008h
  loc_00419F96: mov edx, esp
  loc_00419F98: mov eax, 004075E0h
  loc_00419F9D: push 00000001h
  loc_00419F9F: push 004075B4h ; "AddItem"
  loc_00419FA4: mov [edx], ecx
  loc_00419FA6: mov [edx+00000004h], edi
  loc_00419FA9: mov [edx+00000008h], eax
  loc_00419FAC: mov eax, var_14
  loc_00419FAF: push eax
  loc_00419FB0: mov [edx+0000000Ch], ebx
  loc_00419FB3: call __vbaLateMemCall
  loc_00419FB5: add esp, 0000000Ch
  loc_00419FB8: mov ecx, 00000008h
  loc_00419FBD: mov edx, esp
  loc_00419FBF: mov eax, 004075E8h
  loc_00419FC4: push 00000001h
  loc_00419FC6: push 004075B4h ; "AddItem"
  loc_00419FCB: mov [edx], ecx
  loc_00419FCD: mov [edx+00000004h], edi
  loc_00419FD0: mov [edx+00000008h], eax
  loc_00419FD3: mov eax, var_14
  loc_00419FD6: push eax
  loc_00419FD7: mov [edx+0000000Ch], ebx
  loc_00419FDA: call __vbaLateMemCall
  loc_00419FDC: add esp, 0000000Ch
  loc_00419FDF: mov ecx, 00000008h
  loc_00419FE4: mov edx, esp
  loc_00419FE6: mov eax, 004075F0h
  loc_00419FEB: push 00000001h
  loc_00419FED: push 004075B4h ; "AddItem"
  loc_00419FF2: mov [edx], ecx
  loc_00419FF4: mov [edx+00000004h], edi
  loc_00419FF7: mov [edx+00000008h], eax
  loc_00419FFA: mov eax, var_14
  loc_00419FFD: push eax
  loc_00419FFE: mov [edx+0000000Ch], ebx
  loc_0041A001: call __vbaLateMemCall
  loc_0041A003: add esp, 0000000Ch
  loc_0041A006: mov ecx, 00000008h
  loc_0041A00B: mov edx, esp
  loc_0041A00D: mov eax, 004075F8h
  loc_0041A012: push 00000001h
  loc_0041A014: push 004075B4h ; "AddItem"
  loc_0041A019: mov [edx], ecx
  loc_0041A01B: mov [edx+00000004h], edi
  loc_0041A01E: mov [edx+00000008h], eax
  loc_0041A021: mov eax, var_14
  loc_0041A024: push eax
  loc_0041A025: mov [edx+0000000Ch], ebx
  loc_0041A028: call __vbaLateMemCall
  loc_0041A02A: add esp, 0000000Ch
  loc_0041A02D: mov ecx, 00000008h
  loc_0041A032: mov edx, esp
  loc_0041A034: mov eax, 00406D08h
  loc_0041A039: push 00000001h
  loc_0041A03B: push 004075B4h ; "AddItem"
  loc_0041A040: mov [edx], ecx
  loc_0041A042: mov [edx+00000004h], edi
  loc_0041A045: mov [edx+00000008h], eax
  loc_0041A048: mov eax, var_14
  loc_0041A04B: push eax
  loc_0041A04C: mov [edx+0000000Ch], ebx
  loc_0041A04F: call __vbaLateMemCall
  loc_0041A051: add esp, 0000000Ch
  loc_0041A054: mov ecx, 00000008h
  loc_0041A059: mov edx, esp
  loc_0041A05B: mov eax, 00405FD0h ; "10"
  loc_0041A060: push 00000001h
  loc_0041A062: mov [edx], ecx
  loc_0041A064: mov [edx+00000004h], edi
  loc_0041A067: mov [edx+00000008h], eax
  loc_0041A06A: mov [edx+0000000Ch], ebx
  loc_0041A06D: mov eax, var_14
  loc_0041A070: push 004075B4h ; "AddItem"
  loc_0041A075: push eax
  loc_0041A076: call __vbaLateMemCall
  loc_0041A078: add esp, 0000000Ch
  loc_0041A07B: mov ecx, 00000008h
  loc_0041A080: mov edx, esp
  loc_0041A082: mov eax, 0040678Ch ; "11"
  loc_0041A087: push 00000001h
  loc_0041A089: push 004075B4h ; "AddItem"
  loc_0041A08E: mov [edx], ecx
  loc_0041A090: mov [edx+00000004h], edi
  loc_0041A093: mov [edx+00000008h], eax
  loc_0041A096: mov eax, var_14
  loc_0041A099: push eax
  loc_0041A09A: mov [edx+0000000Ch], ebx
  loc_0041A09D: call __vbaLateMemCall
  loc_0041A09F: add esp, 0000000Ch
  loc_0041A0A2: mov ecx, 00000008h
  loc_0041A0A7: mov edx, esp
  loc_0041A0A9: mov eax, 00406204h ; "12"
  loc_0041A0AE: push 00000001h
  loc_0041A0B0: push 004075B4h ; "AddItem"
  loc_0041A0B5: mov [edx], ecx
  loc_0041A0B7: mov [edx+00000004h], edi
  loc_0041A0BA: mov [edx+00000008h], eax
  loc_0041A0BD: mov eax, var_14
  loc_0041A0C0: push eax
  loc_0041A0C1: mov [edx+0000000Ch], ebx
  loc_0041A0C4: call __vbaLateMemCall
  loc_0041A0C6: add esp, 0000000Ch
  loc_0041A0C9: mov ecx, 00000008h
  loc_0041A0CE: mov edx, esp
  loc_0041A0D0: mov eax, 00407600h ; "13"
  loc_0041A0D5: push 00000001h
  loc_0041A0D7: push 004075B4h ; "AddItem"
  loc_0041A0DC: mov [edx], ecx
  loc_0041A0DE: mov [edx+00000004h], edi
  loc_0041A0E1: mov [edx+00000008h], eax
  loc_0041A0E4: mov eax, var_14
  loc_0041A0E7: push eax
  loc_0041A0E8: mov [edx+0000000Ch], ebx
  loc_0041A0EB: call __vbaLateMemCall
  loc_0041A0ED: add esp, 0000000Ch
  loc_0041A0F0: mov ecx, 00000008h
  loc_0041A0F5: mov edx, esp
  loc_0041A0F7: mov eax, 0040760Ch ; "14"
  loc_0041A0FC: push 00000001h
  loc_0041A0FE: push 004075B4h ; "AddItem"
  loc_0041A103: mov [edx], ecx
  loc_0041A105: mov [edx+00000004h], edi
  loc_0041A108: mov [edx+00000008h], eax
  loc_0041A10B: mov eax, var_14
  loc_0041A10E: push eax
  loc_0041A10F: mov [edx+0000000Ch], ebx
  loc_0041A112: call __vbaLateMemCall
  loc_0041A114: add esp, 0000000Ch
  loc_0041A117: mov ecx, 00000008h
  loc_0041A11C: mov edx, esp
  loc_0041A11E: mov eax, 00407618h ; "15"
  loc_0041A123: push 00000001h
  loc_0041A125: push 004075B4h ; "AddItem"
  loc_0041A12A: mov [edx], ecx
  loc_0041A12C: mov [edx+00000004h], edi
  loc_0041A12F: mov [edx+00000008h], eax
  loc_0041A132: mov eax, var_14
  loc_0041A135: push eax
  loc_0041A136: mov [edx+0000000Ch], ebx
  loc_0041A139: call __vbaLateMemCall
  loc_0041A13B: add esp, 0000000Ch
  loc_0041A13E: mov ecx, 00000008h
  loc_0041A143: mov edx, esp
  loc_0041A145: mov eax, 00407624h ; "16"
  loc_0041A14A: push 00000001h
  loc_0041A14C: push 004075B4h ; "AddItem"
  loc_0041A151: mov [edx], ecx
  loc_0041A153: mov [edx+00000004h], edi
  loc_0041A156: mov [edx+00000008h], eax
  loc_0041A159: mov eax, var_14
  loc_0041A15C: push eax
  loc_0041A15D: mov [edx+0000000Ch], ebx
  loc_0041A160: call __vbaLateMemCall
  loc_0041A162: add esp, 0000000Ch
  loc_0041A165: mov ecx, 00000008h
  loc_0041A16A: mov edx, esp
  loc_0041A16C: mov eax, 00407630h ; "17"
  loc_0041A171: push 00000001h
  loc_0041A173: push 004075B4h ; "AddItem"
  loc_0041A178: mov [edx], ecx
  loc_0041A17A: mov [edx+00000004h], edi
  loc_0041A17D: mov [edx+00000008h], eax
  loc_0041A180: mov eax, var_14
  loc_0041A183: push eax
  loc_0041A184: mov [edx+0000000Ch], ebx
  loc_0041A187: call __vbaLateMemCall
  loc_0041A189: add esp, 0000000Ch
  loc_0041A18C: mov ecx, 00000008h
  loc_0041A191: mov edx, esp
  loc_0041A193: mov eax, 0040763Ch ; "18"
  loc_0041A198: push 00000001h
  loc_0041A19A: push 004075B4h ; "AddItem"
  loc_0041A19F: mov [edx], ecx
  loc_0041A1A1: mov [edx+00000004h], edi
  loc_0041A1A4: mov [edx+00000008h], eax
  loc_0041A1A7: mov eax, var_14
  loc_0041A1AA: push eax
  loc_0041A1AB: mov [edx+0000000Ch], ebx
  loc_0041A1AE: call __vbaLateMemCall
  loc_0041A1B0: add esp, 0000000Ch
  loc_0041A1B3: mov ecx, 00000008h
  loc_0041A1B8: mov edx, esp
  loc_0041A1BA: mov eax, 00407648h ; "19"
  loc_0041A1BF: push 00000001h
  loc_0041A1C1: push 004075B4h ; "AddItem"
  loc_0041A1C6: mov [edx], ecx
  loc_0041A1C8: mov [edx+00000004h], edi
  loc_0041A1CB: mov [edx+00000008h], eax
  loc_0041A1CE: mov eax, var_14
  loc_0041A1D1: push eax
  loc_0041A1D2: mov [edx+0000000Ch], ebx
  loc_0041A1D5: call __vbaLateMemCall
  loc_0041A1D7: add esp, 0000000Ch
  loc_0041A1DA: mov ecx, 00000008h
  loc_0041A1DF: mov edx, esp
  loc_0041A1E1: mov eax, 00407654h ; "20"
  loc_0041A1E6: push 00000001h
  loc_0041A1E8: push 004075B4h ; "AddItem"
  loc_0041A1ED: mov [edx], ecx
  loc_0041A1EF: mov [edx+00000004h], edi
  loc_0041A1F2: mov [edx+00000008h], eax
  loc_0041A1F5: mov eax, var_14
  loc_0041A1F8: push eax
  loc_0041A1F9: mov [edx+0000000Ch], ebx
  loc_0041A1FC: call __vbaLateMemCall
  loc_0041A1FE: add esp, 0000000Ch
  loc_0041A201: mov ecx, 00000008h
  loc_0041A206: mov edx, esp
  loc_0041A208: mov eax, 00407660h ; "25"
  loc_0041A20D: push 00000001h
  loc_0041A20F: push 004075B4h ; "AddItem"
  loc_0041A214: mov [edx], ecx
  loc_0041A216: mov [edx+00000004h], edi
  loc_0041A219: mov [edx+00000008h], eax
  loc_0041A21C: mov eax, var_14
  loc_0041A21F: push eax
  loc_0041A220: mov [edx+0000000Ch], ebx
  loc_0041A223: call __vbaLateMemCall
  loc_0041A225: add esp, 0000000Ch
  loc_0041A228: mov ecx, 00000008h
  loc_0041A22D: mov edx, esp
  loc_0041A22F: mov eax, 0040766Ch ; "30"
  loc_0041A234: push 00000001h
  loc_0041A236: push 004075B4h ; "AddItem"
  loc_0041A23B: mov [edx], ecx
  loc_0041A23D: mov [edx+00000004h], edi
  loc_0041A240: mov [edx+00000008h], eax
  loc_0041A243: mov eax, var_14
  loc_0041A246: push eax
  loc_0041A247: mov [edx+0000000Ch], ebx
  loc_0041A24A: call __vbaLateMemCall
  loc_0041A24C: mov eax, 00407678h ; "35"
  loc_0041A251: mov ecx, 00000008h
  loc_0041A256: add esp, 0000000Ch
  loc_0041A259: mov edx, esp
  loc_0041A25B: push 00000001h
  loc_0041A25D: push 004075B4h ; "AddItem"
  loc_0041A262: mov [edx], ecx
  loc_0041A264: mov [edx+00000004h], edi
  loc_0041A267: mov [edx+00000008h], eax
  loc_0041A26A: mov eax, var_14
  loc_0041A26D: push eax
  loc_0041A26E: mov [edx+0000000Ch], ebx
  loc_0041A271: call __vbaLateMemCall
  loc_0041A273: add esp, 0000000Ch
  loc_0041A276: mov ecx, 00000008h
  loc_0041A27B: mov edx, esp
  loc_0041A27D: mov eax, 00407684h ; "40"
  loc_0041A282: push 00000001h
  loc_0041A284: push 004075B4h ; "AddItem"
  loc_0041A289: mov [edx], ecx
  loc_0041A28B: mov [edx+00000004h], edi
  loc_0041A28E: mov [edx+00000008h], eax
  loc_0041A291: mov eax, var_14
  loc_0041A294: push eax
  loc_0041A295: mov [edx+0000000Ch], ebx
  loc_0041A298: call __vbaLateMemCall
  loc_0041A29A: add esp, 0000000Ch
  loc_0041A29D: mov ecx, 00000008h
  loc_0041A2A2: mov edx, esp
  loc_0041A2A4: mov eax, 00407690h ; "45"
  loc_0041A2A9: push 00000001h
  loc_0041A2AB: push 004075B4h ; "AddItem"
  loc_0041A2B0: mov [edx], ecx
  loc_0041A2B2: mov [edx+00000004h], edi
  loc_0041A2B5: mov [edx+00000008h], eax
  loc_0041A2B8: mov eax, var_14
  loc_0041A2BB: push eax
  loc_0041A2BC: mov [edx+0000000Ch], ebx
  loc_0041A2BF: call __vbaLateMemCall
  loc_0041A2C1: add esp, 0000000Ch
  loc_0041A2C4: mov ecx, 00000008h
  loc_0041A2C9: mov edx, esp
  loc_0041A2CB: mov eax, 0040769Ch ; "50"
  loc_0041A2D0: push 00000001h
  loc_0041A2D2: push 004075B4h ; "AddItem"
  loc_0041A2D7: mov [edx], ecx
  loc_0041A2D9: mov [edx+00000004h], edi
  loc_0041A2DC: mov [edx+00000008h], eax
  loc_0041A2DF: mov eax, var_14
  loc_0041A2E2: push eax
  loc_0041A2E3: mov [edx+0000000Ch], ebx
  loc_0041A2E6: call __vbaLateMemCall
  loc_0041A2E8: add esp, 0000000Ch
  loc_0041A2EB: mov ecx, 00000008h
  loc_0041A2F0: mov edx, esp
  loc_0041A2F2: mov eax, 004076A8h ; "55"
  loc_0041A2F7: push 00000001h
  loc_0041A2F9: push 004075B4h ; "AddItem"
  loc_0041A2FE: mov [edx], ecx
  loc_0041A300: mov [edx+00000004h], edi
  loc_0041A303: mov [edx+00000008h], eax
  loc_0041A306: mov eax, var_14
  loc_0041A309: push eax
  loc_0041A30A: mov [edx+0000000Ch], ebx
  loc_0041A30D: call __vbaLateMemCall
  loc_0041A30F: add esp, 0000000Ch
  loc_0041A312: mov ecx, 00000008h
  loc_0041A317: mov edx, esp
  loc_0041A319: mov eax, 004076B4h ; "60"
  loc_0041A31E: push 00000001h
  loc_0041A320: push 004075B4h ; "AddItem"
  loc_0041A325: mov [edx], ecx
  loc_0041A327: mov [edx+00000004h], edi
  loc_0041A32A: mov [edx+00000008h], eax
  loc_0041A32D: mov eax, var_14
  loc_0041A330: push eax
  loc_0041A331: mov [edx+0000000Ch], ebx
  loc_0041A334: call __vbaLateMemCall
  loc_0041A336: add esp, 0000000Ch
  loc_0041A339: mov ecx, 00000008h
  loc_0041A33E: mov edx, esp
  loc_0041A340: mov eax, 004076C0h ; "65"
  loc_0041A345: mov [edx], ecx
  loc_0041A347: mov [edx+00000004h], edi
  loc_0041A34A: push 00000001h
  loc_0041A34C: push 004075B4h ; "AddItem"
  loc_0041A351: mov [edx+00000008h], eax
  loc_0041A354: mov eax, var_14
  loc_0041A357: push eax
  loc_0041A358: mov [edx+0000000Ch], ebx
  loc_0041A35B: call __vbaLateMemCall
  loc_0041A35D: add esp, 0000000Ch
  loc_0041A360: mov ecx, 00000008h
  loc_0041A365: mov edx, esp
  loc_0041A367: mov eax, 004076CCh ; "70"
  loc_0041A36C: push 00000001h
  loc_0041A36E: push 004075B4h ; "AddItem"
  loc_0041A373: mov [edx], ecx
  loc_0041A375: mov [edx+00000004h], edi
  loc_0041A378: mov [edx+00000008h], eax
  loc_0041A37B: mov eax, var_14
  loc_0041A37E: push eax
  loc_0041A37F: mov [edx+0000000Ch], ebx
  loc_0041A382: call __vbaLateMemCall
  loc_0041A384: add esp, 0000000Ch
  loc_0041A387: mov ecx, 00000008h
  loc_0041A38C: mov edx, esp
  loc_0041A38E: mov eax, 004076D8h ; "75"
  loc_0041A393: push 00000001h
  loc_0041A395: push 004075B4h ; "AddItem"
  loc_0041A39A: mov [edx], ecx
  loc_0041A39C: mov [edx+00000004h], edi
  loc_0041A39F: mov [edx+00000008h], eax
  loc_0041A3A2: mov eax, var_14
  loc_0041A3A5: push eax
  loc_0041A3A6: mov [edx+0000000Ch], ebx
  loc_0041A3A9: call __vbaLateMemCall
  loc_0041A3AB: add esp, 0000000Ch
  loc_0041A3AE: mov ecx, 00000008h
  loc_0041A3B3: mov edx, esp
  loc_0041A3B5: mov eax, 004076E4h ; "80"
  loc_0041A3BA: push 00000001h
  loc_0041A3BC: push 004075B4h ; "AddItem"
  loc_0041A3C1: mov [edx], ecx
  loc_0041A3C3: mov [edx+00000004h], edi
  loc_0041A3C6: mov [edx+00000008h], eax
  loc_0041A3C9: mov eax, var_14
  loc_0041A3CC: push eax
  loc_0041A3CD: mov [edx+0000000Ch], ebx
  loc_0041A3D0: call __vbaLateMemCall
  loc_0041A3D2: add esp, 0000000Ch
  loc_0041A3D5: mov ecx, 00000008h
  loc_0041A3DA: mov edx, esp
  loc_0041A3DC: mov eax, 004076F0h ; "85"
  loc_0041A3E1: push 00000001h
  loc_0041A3E3: push 004075B4h ; "AddItem"
  loc_0041A3E8: mov [edx], ecx
  loc_0041A3EA: mov [edx+00000004h], edi
  loc_0041A3ED: mov [edx+00000008h], eax
  loc_0041A3F0: mov eax, var_14
  loc_0041A3F3: push eax
  loc_0041A3F4: mov [edx+0000000Ch], ebx
  loc_0041A3F7: call __vbaLateMemCall
  loc_0041A3F9: add esp, 0000000Ch
  loc_0041A3FC: mov ecx, 00000008h
  loc_0041A401: mov edx, esp
  loc_0041A403: mov eax, 004076FCh ; "90"
  loc_0041A408: push 00000001h
  loc_0041A40A: push 004075B4h ; "AddItem"
  loc_0041A40F: mov [edx], ecx
  loc_0041A411: mov [edx+00000004h], edi
  loc_0041A414: mov [edx+00000008h], eax
  loc_0041A417: mov eax, var_14
  loc_0041A41A: push eax
  loc_0041A41B: mov [edx+0000000Ch], ebx
  loc_0041A41E: call __vbaLateMemCall
  loc_0041A420: add esp, 0000000Ch
  loc_0041A423: mov ecx, 00000008h
  loc_0041A428: mov edx, esp
  loc_0041A42A: mov eax, 00407708h ; "95"
  loc_0041A42F: mov [edx], ecx
  loc_0041A431: mov [edx+00000004h], edi
  loc_0041A434: mov [edx+00000008h], eax
  loc_0041A437: mov [edx+0000000Ch], ebx
  loc_0041A43A: mov eax, var_14
  loc_0041A43D: push 00000001h
  loc_0041A43F: push 004075B4h ; "AddItem"
  loc_0041A444: push eax
  loc_0041A445: call __vbaLateMemCall
  loc_0041A447: add esp, 0000000Ch
  loc_0041A44A: mov ecx, 00000008h
  loc_0041A44F: mov edx, esp
  loc_0041A451: mov eax, 00407714h ; "100"
  loc_0041A456: push 00000001h
  loc_0041A458: push 004075B4h ; "AddItem"
  loc_0041A45D: mov [edx], ecx
  loc_0041A45F: mov [edx+00000004h], edi
  loc_0041A462: mov [edx+00000008h], eax
  loc_0041A465: mov eax, var_14
  loc_0041A468: push eax
  loc_0041A469: mov [edx+0000000Ch], ebx
  loc_0041A46C: call __vbaLateMemCall
  loc_0041A46E: add esp, 0000000Ch
  loc_0041A471: mov ecx, 00000002h
  loc_0041A476: mov edx, esp
  loc_0041A478: mov eax, 00000004h
  loc_0041A47D: push 0040771Ch ; "ListIndex"
  loc_0041A482: mov [edx], ecx
  loc_0041A484: mov [edx+00000004h], edi
  loc_0041A487: mov [edx+00000008h], eax
  loc_0041A48A: mov eax, var_14
  loc_0041A48D: push eax
  loc_0041A48E: mov [edx+0000000Ch], ebx
  loc_0041A491: call [00401068h] ; __vbaLateMemSt
  loc_0041A497: push 00405B4Ch
  loc_0041A49C: push 00000000h
  loc_0041A49E: call [004011D4h] ; __vbaCastObj
  loc_0041A4A4: mov esi, [00401080h] ; __vbaObjSet
  loc_0041A4AA: lea ecx, var_14
  loc_0041A4AD: push eax
  loc_0041A4AE: push ecx
  loc_0041A4AF: call __vbaObjSet
  loc_0041A4B1: mov edi, Me
  loc_0041A4B4: push edi
  loc_0041A4B5: mov edx, [edi]
  loc_0041A4B7: call [edx+00000320h]
  loc_0041A4BD: push eax
  loc_0041A4BE: lea eax, var_20
  loc_0041A4C1: push eax
  loc_0041A4C2: call __vbaObjSet
  loc_0041A4C4: mov esi, eax
  loc_0041A4C6: push 00000050h
  loc_0041A4C8: mov ebx, [esi]
  loc_0041A4CA: call [00401004h] ; __vbaStrI2
  loc_0041A4D0: mov edx, eax
  loc_0041A4D2: lea ecx, var_1C
  loc_0041A4D5: call [004011D0h] ; __vbaStrMove
  loc_0041A4DB: push eax
  loc_0041A4DC: push esi
  loc_0041A4DD: call [ebx+000000A4h]
  loc_0041A4E3: test eax, eax
  loc_0041A4E5: fnclex
  loc_0041A4E7: jge 0041A4FBh
  loc_0041A4E9: push 000000A4h
  loc_0041A4EE: push 00405398h
  loc_0041A4F3: push esi
  loc_0041A4F4: push eax
  loc_0041A4F5: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041A4FB: mov esi, [004011F4h] ; __vbaFreeStr
  loc_0041A501: lea ecx, var_1C
  loc_0041A504: call __vbaFreeStr
  loc_0041A506: lea ecx, var_20
  loc_0041A509: call [004011F0h] ; __vbaFreeObj
  loc_0041A50F: mov ecx, [edi]
  loc_0041A511: push edi
  loc_0041A512: call [ecx+0000031Ch]
  loc_0041A518: lea edx, var_20
  loc_0041A51B: push eax
  loc_0041A51C: push edx
  loc_0041A51D: call [00401080h] ; __vbaObjSet
  loc_0041A523: mov ebx, [eax]
  loc_0041A525: push 00000064h
  loc_0041A527: mov var_44, eax
  loc_0041A52A: call [00401004h] ; __vbaStrI2
  loc_0041A530: mov edx, eax
  loc_0041A532: lea ecx, var_1C
  loc_0041A535: call [004011D0h] ; __vbaStrMove
  loc_0041A53B: mov var_50, ebx
  loc_0041A53E: mov ebx, var_44
  loc_0041A541: push eax
  loc_0041A542: mov eax, var_50
  loc_0041A545: push ebx
  loc_0041A546: call [eax+000000A4h]
  loc_0041A54C: test eax, eax
  loc_0041A54E: fnclex
  loc_0041A550: jge 0041A564h
  loc_0041A552: push 000000A4h
  loc_0041A557: push 00405398h
  loc_0041A55C: push ebx
  loc_0041A55D: push eax
  loc_0041A55E: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041A564: lea ecx, var_1C
  loc_0041A567: call __vbaFreeStr
  loc_0041A569: lea ecx, var_20
  loc_0041A56C: call [004011F0h] ; __vbaFreeObj
  loc_0041A572: mov ecx, [edi]
  loc_0041A574: push edi
  loc_0041A575: call [ecx+00000318h]
  loc_0041A57B: lea edx, var_20
  loc_0041A57E: push eax
  loc_0041A57F: push edx
  loc_0041A580: call [00401080h] ; __vbaObjSet
  loc_0041A586: mov ebx, [eax]
  loc_0041A588: push 00000078h
  loc_0041A58A: mov var_44, eax
  loc_0041A58D: call [00401004h] ; __vbaStrI2
  loc_0041A593: mov edx, eax
  loc_0041A595: lea ecx, var_1C
  loc_0041A598: call [004011D0h] ; __vbaStrMove
  loc_0041A59E: mov var_54, ebx
  loc_0041A5A1: mov ebx, var_44
  loc_0041A5A4: push eax
  loc_0041A5A5: mov eax, var_54
  loc_0041A5A8: push ebx
  loc_0041A5A9: call [eax+000000A4h]
  loc_0041A5AF: test eax, eax
  loc_0041A5B1: fnclex
  loc_0041A5B3: jge 0041A5C7h
  loc_0041A5B5: push 000000A4h
  loc_0041A5BA: push 00405398h
  loc_0041A5BF: push ebx
  loc_0041A5C0: push eax
  loc_0041A5C1: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041A5C7: lea ecx, var_1C
  loc_0041A5CA: call __vbaFreeStr
  loc_0041A5CC: lea ecx, var_20
  loc_0041A5CF: call [004011F0h] ; __vbaFreeObj
  loc_0041A5D5: mov ecx, [edi]
  loc_0041A5D7: push edi
  loc_0041A5D8: call [ecx+00000310h]
  loc_0041A5DE: lea edx, var_20
  loc_0041A5E1: push eax
  loc_0041A5E2: push edx
  loc_0041A5E3: call [00401080h] ; __vbaObjSet
  loc_0041A5E9: mov ebx, [eax]
  loc_0041A5EB: push 00000004h
  loc_0041A5ED: mov var_44, eax
  loc_0041A5F0: call [00401004h] ; __vbaStrI2
  loc_0041A5F6: mov edx, eax
  loc_0041A5F8: lea ecx, var_1C
  loc_0041A5FB: call [004011D0h] ; __vbaStrMove
  loc_0041A601: mov var_58, ebx
  loc_0041A604: mov ebx, var_44
  loc_0041A607: push eax
  loc_0041A608: mov eax, var_58
  loc_0041A60B: push ebx
  loc_0041A60C: call [eax+000000A4h]
  loc_0041A612: test eax, eax
  loc_0041A614: fnclex
  loc_0041A616: jge 0041A62Ah
  loc_0041A618: push 000000A4h
  loc_0041A61D: push 00405398h
  loc_0041A622: push ebx
  loc_0041A623: push eax
  loc_0041A624: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041A62A: lea ecx, var_1C
  loc_0041A62D: call __vbaFreeStr
  loc_0041A62F: lea ecx, var_20
  loc_0041A632: call [004011F0h] ; __vbaFreeObj
  loc_0041A638: mov ecx, [edi]
  loc_0041A63A: push edi
  loc_0041A63B: call [ecx+0000030Ch]
  loc_0041A641: lea edx, var_20
  loc_0041A644: push eax
  loc_0041A645: push edx
  loc_0041A646: call [00401080h] ; __vbaObjSet
  loc_0041A64C: mov ebx, [eax]
  loc_0041A64E: push 00000002h
  loc_0041A650: mov var_44, eax
  loc_0041A653: call [00401004h] ; __vbaStrI2
  loc_0041A659: mov edx, eax
  loc_0041A65B: lea ecx, var_1C
  loc_0041A65E: call [004011D0h] ; __vbaStrMove
  loc_0041A664: mov var_5C, ebx
  loc_0041A667: mov ebx, var_44
  loc_0041A66A: push eax
  loc_0041A66B: mov eax, var_5C
  loc_0041A66E: push ebx
  loc_0041A66F: call [eax+000000A4h]
  loc_0041A675: test eax, eax
  loc_0041A677: fnclex
  loc_0041A679: jge 0041A68Dh
  loc_0041A67B: push 000000A4h
  loc_0041A680: push 00405398h
  loc_0041A685: push ebx
  loc_0041A686: push eax
  loc_0041A687: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041A68D: lea ecx, var_1C
  loc_0041A690: call __vbaFreeStr
  loc_0041A692: lea ecx, var_20
  loc_0041A695: call [004011F0h] ; __vbaFreeObj
  loc_0041A69B: mov ecx, [edi]
  loc_0041A69D: push edi
  loc_0041A69E: call [ecx+00000314h]
  loc_0041A6A4: lea edx, var_20
  loc_0041A6A7: push eax
  loc_0041A6A8: push edx
  loc_0041A6A9: call [00401080h] ; __vbaObjSet
  loc_0041A6AF: mov edi, eax
  loc_0041A6B1: push 3FF00000h
  loc_0041A6B6: push 00000000h
  loc_0041A6B8: mov ebx, [edi]
  loc_0041A6BA: call [00401104h] ; __vbaStrR8
  loc_0041A6C0: mov edx, eax
  loc_0041A6C2: lea ecx, var_1C
  loc_0041A6C5: call [004011D0h] ; __vbaStrMove
  loc_0041A6CB: push eax
  loc_0041A6CC: push edi
  loc_0041A6CD: call [ebx+000000A4h]
  loc_0041A6D3: test eax, eax
  loc_0041A6D5: fnclex
  loc_0041A6D7: jge 0041A6EBh
  loc_0041A6D9: push 000000A4h
  loc_0041A6DE: push 00405398h
  loc_0041A6E3: push edi
  loc_0041A6E4: push eax
  loc_0041A6E5: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041A6EB: lea ecx, var_1C
  loc_0041A6EE: call __vbaFreeStr
  loc_0041A6F0: lea ecx, var_20
  loc_0041A6F3: call [004011F0h] ; __vbaFreeObj
  loc_0041A6F9: fwait
  loc_0041A6FA: push 0041A71Eh
  loc_0041A6FF: jmp 0041A714h
  loc_0041A701: lea ecx, var_1C
  loc_0041A704: call [004011F4h] ; __vbaFreeStr
  loc_0041A70A: lea ecx, var_20
  loc_0041A70D: call [004011F0h] ; __vbaFreeObj
  loc_0041A713: ret
  loc_0041A714: lea ecx, var_14
  loc_0041A717: call [004011F0h] ; __vbaFreeObj
  loc_0041A71D: ret
  loc_0041A71E: mov eax, arg_C
  loc_0041A721: mov cx, var_18
  loc_0041A725: pop edi
  loc_0041A726: pop esi
  loc_0041A727: mov [eax], cx
  loc_0041A72A: mov ecx, var_10
  loc_0041A72D: xor eax, eax
  loc_0041A72F: mov fs:[00000000h], ecx
  loc_0041A736: pop ebx
  loc_0041A737: mov esp, ebp
  loc_0041A739: pop ebp
  loc_0041A73A: retn 0008h
End Sub
