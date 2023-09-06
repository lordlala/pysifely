Function Get-CurrentEpochTime {

    $DateTime = Get-Date #or any other command to get DateTime object
    
    return ([DateTimeOffset]$DateTime).ToUnixTimeSeconds()

}

Function Get-SifelyToken {

    [cmdletbinding()]
    Param (
        [String]$Username = "**@gmail.com",
        [String]$Password = "((!"
    )

    $Payload = @{
      "username" = $Username
      "password" = $Password
    } | ConvertTo-Json

    $URL = "https://pro-server.sifely.com/login"

    $Headers = @{
        'Content-Type' = 'application/json;charset=UTF-8'
        'User-Agent' = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188'
    }

    $Response = Invoke-WebRequest -Method Post -Uri $Url -Headers $Headers -Body $Payload 

    $Token = ($Response.Content | ConvertFrom-Json).Token

    return $Token
}

Function Get-SifelyInfo {

    [cmdletbinding()]
    Param (
        $Token
    )

    $URL = "https://pro-server.sifely.com/getInfo"

    $Headers = @{
        'Accept' = 'application/json, text/plain, */*'
        'Accept-Encoding' = 'gzip, deflate, br'
        'Accept-Language' = 'en-US,en;q=0.9'
        'Authorization' = "Bearer $Token"
    }

    $Response = Invoke-WebRequest -Method Get -Uri $Url -Headers $Headers
    
    return $Response 
}

Function Get-SifelyGatewayList {

    [cmdletbinding()]
    Param (
        $Token
    )

    $URL = 'https://pro-server.sifely.com/v3/gateway/list'

    $Headers = @{
        'Accept' = 'application/json, text/plain, */*'
        'Accept-Encoding' = 'gzip, deflate, br'
        'Accept-Language' = 'en-US,en;q=0.9'
        'Authorization' = "Bearer $Token"
    }

    $Payload = @{
        'groupId' = '0'
        'pageNo' = '1' 
        'pageSize' =' 10'
    } #| ConvertTo-Json

    $Response = Invoke-WebRequest -Method Post -Uri $Url -Headers $Headers -Body $Payload
    
    return ($Response.Content | ConvertFrom-Json)
}

Function Get-SifelyGroupByForLock {
    
    [cmdletbinding()]
    Param (
        $Token
    )

    $URL = 'https://pro-server.sifely.com/v3/lock/getGroupByForLock'

    $Headers = @{
        'Accept' = 'application/json, text/plain, */*'
        'Accept-Encoding' = 'gzip, deflate, br'
        'Accept-Language' = 'en-US,en;q=0.9'
        'Authorization' = "Bearer $Token"
    }

    $Response = Invoke-WebRequest -Method Post -Uri $Url -Headers $Headers
    
    return ($Response.Content | ConvertFrom-Json)
}

Function Get-SifelyLockByGroupId {
    [cmdletbinding()]
    Param (
        $Token
    )

    $URL = 'https://pro-server.sifely.com/v3/lock/getLockByGroupId'

    $Headers = @{
        'Accept' = 'application/json, text/plain, */*'
        'Accept-Encoding' = 'gzip, deflate, br'
        'Accept-Language' = 'en-US,en;q=0.9'
        'Authorization' = "Bearer $Token"
        'Content-Type' = 'application/x-www-form-urlencoded'
    }

    $Payload = @{
        'groupId' = '0'
        'pageNo' = '1' 
        'pageSize' =' 10'
    } #| ConvertTo-Json

    $Response = Invoke-WebRequest -Method Post -Uri $Url -Headers $Headers -Body $Payload 
    
    return ($Response.Content | ConvertFrom-Json)
}

Function Get-SifelyLockState {
    [cmdletbinding()]
    Param (
        $Token,
        $Lock
    )

    $URL = 'https://pro-server.sifely.com/v3/lock/queryOpenState'

    $Headers = @{
        'Accept' = 'application/json, text/plain, */*'
        'Accept-Encoding' = 'gzip, deflate, br'
        'Accept-Language' = 'en-US,en;q=0.9'
        'Authorization' = "Bearer $Token"
        'Content-Type' = 'application/x-www-form-urlencoded'
    }

    $Payload = @{
        'lockId' = $Lock.data.list.lockId
         'date' = $Lock.data.list.Date
    }

    $Response = Invoke-WebRequest -Method Post -Uri $Url -Headers $Headers -Body $Payload 
    
    #state:0 means locked

    return $Response # ($Response.Content | ConvertFrom-Json)
}

Function Set-SifelyAutolockTime {
    [cmdletbinding(DefaultParameterSetName='Default')]
    Param (

        [Parameter(Mandatory=$True, ParameterSetName='Default')]
        [Parameter(ParameterSetName='Disabled')]
        $Token,
        [Parameter(Mandatory=$True, ParameterSetName='Default')]
        [Parameter(ParameterSetName='Disabled')]
        $Lock,
        [Parameter(ParameterSetName='Disabled')]
        [Switch]$Disabled
    )
    
    $URL = "https://pro-server.sifely.com/v3/lock/setAutoLockTime"

    write-host $URL

    $Headers = @{
        'Accept' = 'application/json, text/plain, */*'
        'Accept-Encoding' = 'gzip, deflate, br'
        'Accept-Language' = 'en-US,en;q=0.9'
        'Authorization' = "Bearer $Token"
        'Content-Type' = 'application/x-www-form-urlencoded'
    }


    
    #state:0 means locked



    Switch ($PSCmdlet.ParameterSetName) {

        Disabled {
            $Payload = @{
                'lockId' = $Lock.data.list.lockId
                'date' = $Lock.data.list.Date
                'seconds' = '0'
                'type' = '2'
            }

            $Response = Invoke-WebRequest -Method Post -Uri $Url -Headers $Headers -Body $Payload 

            return $response #($Response.Content | ConvertFrom-Json)
        }

        Default {

           Return "Default"

        }

    }
        
}

Function Set-SifelyLockState {
    [cmdletbinding()]
    Param (
        $Token,
        $Lock,
        [ValidateSet('Lock','Unlock')]
        [String]$State
    )

    $URL = "https://pro-server.sifely.com/v3/lock/$($state.ToLower())"

    write-host $URL

    $Headers = @{
        'Accept' = 'application/json, text/plain, */*'
        'Accept-Encoding' = 'gzip, deflate, br'
        'Accept-Language' = 'en-US,en;q=0.9'
        'Authorization' = "Bearer $Token"
        'Content-Type' = 'application/x-www-form-urlencoded'
    }

    $Payload = @{
        'lockId' = $Lock.data.list.lockId
         'date' = $Lock.data.list.Date
    }

    $Response = Invoke-WebRequest -Method Post -Uri $Url -Headers $Headers -Body $Payload 
    
    #state:0 means locked

    return $response #($Response.Content | ConvertFrom-Json)
}

Function Invoke-SifelyLock {
    [cmdletbinding()]
    Param (
        $Token,
        $Lock
    )

    $URL = 'https://pro-server.sifely.com/v3/lock/lock'

    $Headers = @{
        'Accept' = 'application/json, text/plain, */*'
        'Accept-Encoding' = 'gzip, deflate, br'
        'Accept-Language' = 'en-US,en;q=0.9'
        'Authorization' = "Bearer $Token"
        'Content-Type' = 'application/x-www-form-urlencoded'
    }

    $Payload = @{
        'lockId' = $Lock.data.list.lockId
         'date' = $Lock.data.list.Date
    }

    $Response = Invoke-WebRequest -Method Post -Uri $Url -Headers $Headers -Body $Payload 
    
    #state:0 means locked

    return ($Response.Content | ConvertFrom-Json)
}


$Token = Get-SifelyToken
#$Info = Get-SifelyInfo -Token $Token
#$SifelyGroupByForLock = Get-SifelyGroupByForLock -Token $Token
$SifelyLockByGroupId = Get-SifelyLockByGroupId -Token $Token
#$Lock = Get-SifelyLockState -Token $Token -Lock $SifelyLockByGroupId
#$Unlock = Invoke-SifelyUnlock -Token $Token -Lock $SifelyLockByGroupId
#$Lock = Invoke-Sifelylock -Token $Token -Lock $SifelyLockByGroupId 
#$Lock = Set-SifelyLockState -Token $Token -Lock $SifelyLockByGroupId -State Lock
#$UnLock = Set-SifelyLockState -Token $Token -Lock $SifelyLockByGroupId -State Unlock
#$Gatewaylist = Get-SifelyGatewayList -Token $Token

Set-SifelyAutolockTime -Token $Token -Lock $SifelyLockByGroupId -Disabled
