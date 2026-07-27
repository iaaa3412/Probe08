# Ask the installed VISA (whatever visa32.dll resolves to) what it can see,
# and try to open the Electroglas at GPIB0::29::INSTR the same way pyvisa would.
$ErrorActionPreference = 'Stop'
$src = @'
using System;
using System.Text;
using System.Runtime.InteropServices;
public static class Visa {
    [DllImport("visa32.dll")] public static extern int viOpenDefaultRM(out uint sesn);
    [DllImport("visa32.dll", CharSet = CharSet.Ansi)]
    public static extern int viFindRsrc(uint sesn, string expr, out uint findList, out uint retCnt, StringBuilder desc);
    [DllImport("visa32.dll")] public static extern int viFindNext(uint findList, StringBuilder desc);
    [DllImport("visa32.dll", CharSet = CharSet.Ansi)]
    public static extern int viOpen(uint sesn, string name, uint mode, uint timeout, out uint vi);
    [DllImport("visa32.dll")] public static extern int viClose(uint vi);
    [DllImport("visa32.dll")] public static extern int viStatusDesc(uint vi, int status, StringBuilder desc);
    [DllImport("visa32.dll", CharSet = CharSet.Ansi)]
    public static extern int viGetAttribute(uint vi, uint attr, StringBuilder val);
}
'@
Add-Type -TypeDefinition $src -Language CSharp

function Desc([uint32]$s, [int]$status) {
    $sb = New-Object System.Text.StringBuilder 256
    [void][Visa]::viStatusDesc($s, $status, $sb)
    $sb.ToString()
}

$rm = [uint32]0
$st = [Visa]::viOpenDefaultRM([ref]$rm)
if ($st -lt 0) { Write-Output ("viOpenDefaultRM FAILED status=0x{0:X8}" -f $st); exit 1 }
Write-Output ("viOpenDefaultRM OK  rm={0}" -f $rm)

# Which VISA vendor answered?
$sb = New-Object System.Text.StringBuilder 512
$VI_ATTR_RSRC_MANF_NAME = [Convert]::ToUInt32('BFFF0072', 16)
if ([Visa]::viGetAttribute($rm, $VI_ATTR_RSRC_MANF_NAME, $sb) -ge 0) {
    Write-Output ("VISA vendor: " + $sb.ToString())
}

foreach ($expr in @('?*INSTR', 'GPIB?*INSTR')) {
    Write-Output ("--- viFindRsrc '{0}' ---" -f $expr)
    $fl = [uint32]0; $cnt = [uint32]0
    $d = New-Object System.Text.StringBuilder 512
    $st = [Visa]::viFindRsrc($rm, $expr, [ref]$fl, [ref]$cnt, $d)
    if ($st -lt 0) { Write-Output ("  none / error 0x{0:X8}  {1}" -f $st, (Desc $rm $st)); continue }
    Write-Output ("  {0}" -f $d.ToString())
    for ($i = 1; $i -lt $cnt; $i++) {
        $d2 = New-Object System.Text.StringBuilder 512
        if ([Visa]::viFindNext($fl, $d2) -lt 0) { break }
        Write-Output ("  {0}" -f $d2.ToString())
    }
}

Write-Output "--- viOpen GPIB0::29::INSTR (the Electroglas) ---"
$vi = [uint32]0
$st = [Visa]::viOpen($rm, 'GPIB0::29::INSTR', 0, 2000, [ref]$vi)
if ($st -lt 0) {
    Write-Output ("  FAILED status=0x{0:X8}" -f $st)
    Write-Output ("  {0}" -f (Desc $rm $st))
} else {
    Write-Output ("  OPENED vi={0} (status=0x{1:X8})" -f $vi, $st)
    [void][Visa]::viClose($vi)
}
[void][Visa]::viClose($rm)
