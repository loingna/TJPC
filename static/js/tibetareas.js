//显示模态框中的登陆面板
function showLogin(){
    $("#login").addClass("active");
    $("#reg").removeClass("active");
    $("#find").removeClass("active");
    $("#loginpanel").addClass("active");
    $("#regpanel").removeClass("active");
    $('#findpanel').removeClass("active");
    $("#mymodal").modal('show');
}

//显示模态框中的注册面板
function showReg(){
    $("#login").removeClass("active");
    $("#reg").addClass("active");
    $("#find").removeClass("active");
    $("#loginpanel").removeClass("active");
    $("#regpanel").addClass("active");
    $('#findpanel').removeClass("active");
    $("#mymodal").modal('show');
}

function doSendMail(obj){
    var email = $.trim($("#regname").val());
    //对邮箱地址进行校验(xxx@xxx.x)
    if (!email.match(/.+@.+\..+/)){
        alert('邮箱地址格式不正确！请输入正确格式！');
        $("#regname").focus();
        return false;
    }
    $.post('/ecode', 'email=' + email, function (data){
        if(data=='email-invalid'){
            alert('邮箱地址格式不正确！');
            $("#regname").focus();
            return false;
        }
        if(data=='send-pass'){
            alert('邮箱验证码已成功发送，请查收！');
            //验证码发送完成后禁止修改注册邮箱
            $("#regname").attr('disabled', true);
            //发送邮件按钮变为不可用
            $(obj).attr('disabled', true);
            return false;
        }
        else{
            alert('邮箱验证码未发送成功！');
            return false;
        }
    })
}

function doReg(){
    var regname = $.trim($("#regname").val());
    var regpass = $.trim($("#regpass").val());
    var regcode = $.trim($("#regcode").val());

    if (!regname.match(/.+@.+\..+/) || regpass.length < 5){
        alert('注册邮箱不正确或者密码少于5位！');
        return false;
    }else{
        //构建Post请求的正文数据
        param = "username=" + regname;
        param += "&password=" + regpass;
        param += "&ecode=" + regcode;
        //利用jQuery框架发送POST请求，并获取到后台注册接口的响应内容
        $.post('/user', param, function(data){
            if(data == "ecode-error"){
                alert('验证码无效！');
                $("#regcode").val('');
                $("#regcode").focus();
            }else if(data == "up-invalid"){
                alert('注册邮箱不正确或者密码少于5位！');
            }else if(data == "user-repeated"){
                alert('该用户名已经被注册！');
                $("#regname").focus();
            }else if(data == "reg-pass"){
                alert('恭喜你！注册成功！');
                //注册成功后，延迟1秒重新刷新当前页面即可
                setTimeout('location.reload();', 500);
            }else if(data == "reg-fail"){
                alert('注册失败，请联系管理员！');
            }
        });
    }
}

function doLogin(e){
    if(e != null && e.keyCode != 13){
        return false;
    }
    var loginname = $.trim($("#loginname").val());
    var loginpass = $.trim($("#loginpass").val());
    var logincode = $.trim($("#logincode").val());

    if (loginname.length < 5 || loginpass.length < 5){
        alert('用户名和密码少于5位！');
        return false;
    }
    else{
        //构建POST请求的数据
        var param = "username=" + loginname;
        param += "&password=" + loginpass;
        param += "&vcode=" + logincode;
        //利用jQuery框架发送POST请求，并获取后台登录接口的相应内容
        $.post('/login', param, function(data){
            if (data == "vcode-error"){
                alert('验证码无效！');
                $("#logincode").val('');
                $("#logincode").focus();
            }else if(data == "login-pass"){
                alert('恭喜你！登陆成功！');
                setTimeout('location.reload();', 1000);
            }else if(data == "login-fail"){
                alert('登陆失败，请联系管理员！');
            }
        });
    }
}