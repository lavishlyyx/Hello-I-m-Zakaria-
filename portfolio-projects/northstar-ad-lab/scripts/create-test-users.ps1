# REVIEW FIRST. Run only on a disposable ad.northstar.test lab domain.
# Requires the ActiveDirectory PowerShell module and delegated OU creation rights.
# Does NOT create or store user passwords; accounts created disabled.
Import-Module ActiveDirectory -ErrorAction Stop
$domain = (Get-ADDomain).DNSRoot
if ($domain -ne 'ad.northstar.test') {
    throw "Refusing to run: expected isolated lab domain ad.northstar.test; found $domain"
}
$base = (Get-ADDomain).DistinguishedName
$root = "OU=Northstar,$base"
if (-not (Get-ADOrganizationalUnit -LDAPFilter '(ou=Northstar)' -SearchBase $base -SearchScope OneLevel -ErrorAction SilentlyContinue)) {
    New-ADOrganizationalUnit -Name 'Northstar' -Path $base -ProtectedFromAccidentalDeletion $true
}
$usersOU = "OU=Users,$root"
if (-not (Get-ADOrganizationalUnit -Identity $usersOU -ErrorAction SilentlyContinue)) {
    New-ADOrganizationalUnit -Name 'Users' -Path $root -ProtectedFromAccidentalDeletion $true
}
$departments = @('Finance','HR','Sales','IT')
foreach ($d in $departments) {
    $dn = "OU=$d,$usersOU"
    if (-not (Get-ADOrganizationalUnit -Identity $dn -ErrorAction SilentlyContinue)) {
        New-ADOrganizationalUnit -Name $d -Path $usersOU
    }
}
for ($i=1; $i -le 10; $i++) {
    $department = $departments[($i-1) % $departments.Count]
    $sam = ('testuser{0:D2}' -f $i)
    if (-not (Get-ADUser -Filter "SamAccountName -eq '$sam'" -ErrorAction SilentlyContinue)) {
        New-ADUser -Name "Lab User $i" -SamAccountName $sam -Path "OU=$department,$usersOU" -Department $department -Enabled $false -Description 'Fictional portfolio lab account - disabled by default'
        Write-Host "Created disabled account $sam ($department)"
    }
}
Write-Host "Done. No accounts were enabled and no passwords were set."
