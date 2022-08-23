clear;
connClass = py.importlib.import_module('matClient');
conn = connClass.matClient('os3-380-23015.vs.sakura.ne.jp',6379,0);
%os3-380-23015.vs.sakura.ne.jp163.143.132.107
%land(conn);
m = 0;
cnt = 0;
state = 0;
count = 0;
flg = 0;
hgt = 40;
okflg = 0;
q = '';
last = 0;
x2 = 0;
y2 = 0;
A = zeros(720,960);
B = logical(A);
q1 = 0;
q2 = 0;
lefthand = 0;
righthand = 0;
prevlefthand = 0;
prevrighthand = 0;
flag2 = 1;
while 1
    % 画像の取得
    D = conn.fromRedis('image');
    I = rgb2bgr(uint8(D));
    % 情報の取得
    J = conn.fromRedis('state');
    tof = J{'tof'}.int64;
    s = strcat('Battery:', int2str(J{'bat'}.int64), ', ToF:', int2str(J{'tof'}.int64), ', Roll:', int2str(J{'roll'}.int64), ', Pitch:', int2str(J{'pitch'}.int64), ', Yaw:', int2str(J{'yaw'}.int64));
    position =  [1 50];
    value = [s];
    RGB = insertText(I,position,value,'AnchorPoint','LeftBottom');
    position =  [1 50];
    value = [s];
    RGB = insertText(I,position,value,'AnchorPoint','LeftBottom');
    imshow(RGB); % 画面表示
    
    % State 0: 離陸 (tofでhgt[cm])
    if state == 0 
       if(tof< 15)
        takeoff(conn);
        else
        up(conn,20);
        forward(conn,20);
        pause(6);
        
        state = 1;
       end
       %forward(conn,20);
       % if(tof- hgt < 50)
        %    state = 8
        %elseif(tof < 20)
         %  q = takeoff(conn);
          % pause(5);
        %else
         %   if hgt-tof > 20
          %      q = up(conn, hgt-tof);
           % else
                %q = down(conn, 40);
            %end
            
   % end
       %state = 9
       %down(conn,60);
       %forward(conn,30);
       %pause(6);
    % State 1: 窓認識
    elseif state == 1
        d = zeros(5,5);
        % HSV画像の取得
        H = rgb2hsv(I);
        % 赤領域の取得 (5x5)
        %緑
        %
       % B(:,:,1) = ((H(:,:,1) < 0.4) & H(:,:,1) > 0.2) & (H(:,:,2) > 0.5) & (H(:,:,3) > 0.1);
        %青
        B(:,:,1) = ((H(:,:,1) < 0.69) & H(:,:,1) > 0.47) & (H(:,:,2) > 0.5) & (H(:,:,3) > 0.1);
       %会場赤
       %B(:,:,1) = (H(:,:,1) < 0.1 | H(:,:,1) > 0.9) & (H(:,:,2) > 0.5) & (H(:,:,3) > 0.12);
       %B(:,:,1) = (H(:,:,1) < 0.1 | H(:,:,1) > 0.9) & (H(:,:,2) > 0.7) & (H(:,:,3) > 0.30);
        for i=0:1:4
            for j=0:1:4
                d(i+1,j+1)=sum(sum(B(i*int16(720/5)+1:(i+1)*int16(720/5),j*int16(960/5)+1:(j+1)*int16(960/5))));
            end
        end
        % 5x5ビン内の最大値とx,yの取得
        maxd = max(max(d));
        [x,y] = find(d == maxd);
        % 移動のコード
        if maxd < 100
            left(conn,20);
            
        else
            state = 2
        end
    % State 2: 窓通過
    elseif state == 2
        d = zeros(5,5);
        % HSV画像の取得
        H = rgb2hsv(I);
        % 赤領域の取得 (5x5)
        %緑
        %B(:,:,1) = ((H(:,:,1) < 0.4) & H(:,:,1) > 0.2) & (H(:,:,2) > 0.5) & (H(:,:,3) > 0.1);
        %青
        B(:,:,1) = ((H(:,:,1) < 0.69) & H(:,:,1) > 0.47) & (H(:,:,2) > 0.5) & (H(:,:,3) > 0.1);
       % B(:,:,1) = (H(:,:,1) < 0.1 | H(:,:,1) > 0.9) & (H(:,:,2) > 0.5) & (H(:,:,3) > 0.2);
       %B(:,:,1) = (H(:,:,1) < 0.1 | H(:,:,1) > 0.9) & (H(:,:,2) > 0.7) & (H(:,:,3) > 0.30);
        for i=0:1:4
            for j=0:1:4
                d(i+1,j+1)=sum(sum(B(i*int16(720/5)+1:(i+1)*int16(720/5),j*int16(960/5)+1:(j+1)*int16(960/5))));
            end
        end
        imshow(B)
        % 5x5ビン内の最大値とx,yの取得
        maxd = max(max(d));
        [x,y] = find(d == maxd)
        % 移動のコード
        if maxd > 20
            if (y == 2 || y ==1)
                %moveleft(ryzeObj,0.2,1);
                left(conn,20);
            elseif (y==4 || y ==5)
                %moveright(ryzeObj,0.2,1);
                right(conn,20);
            elseif (x==2 || x ==1) && y==3
                %moveup(ryzeObj,0.2,1);
                up(conn,20);
            elseif (x== 5) && y == 3
                %movedown(ryzeObj,0.2,1);
                down(conn,20);
            elseif (x==3 || x ==4) && y==3
                if(maxd < 4000)
                    %moveforward(ryzeObj,0.3,1);
                    forward(conn,30);
                elseif(maxd > 20000)
                    %moveback(ryzeObj,0.3,1);
                    back(conn,30);
                elseif( 4001 < maxd || maxd < 19999 )
                    %moveforward(ryzeObj,2,0.7);
                    pause(5);
                    q = forward(conn,150);
                    %if(strcmp(q, 'ok'))
                    pause(5);
                        state = 8
                    %end
                end
            end
        else 
            %moveback(ryzeObj,0.3,1);
            back(conn,30);
        end
    % elseif state == 3
     %   pause(5);
      %  q = cw(conn,180);
        %if(strcmp(q, 'ok'))
       %     state = 4
        %end
    %elseif state == 4
     %   pause(5);
      %  q = forward(conn,150);
        %if(strcmp(q, 'ok'))
       %     state = 6
        %end
    %% 前移動シーケンス
   % elseif state == 5
    %    pause(5);
     %   q = forward(conn,100);
      %  if(strcmp(q, 'ok'))
       %     state = 6
        %end       
    elseif state == 6
        H = rgb2hsv(I);
        B(:,:,1) = (H(:,:,1) < 0.1 | H(:,:,1) > 0.9) & (H(:,:,2) > 0.7) & (H(:,:,3) > 0.2);
        for i=0:1:2
            for j=0:1:2
                d2(i+1,j+1)=sum(sum(B(i*int16(720/3)+1:(i+1)*int16(720/3),j*int16(960/3)+1:(j+1)*int16(960/3))));
            end
        end
        imshow(B)
        maxd = max(max(d2));
        [x,y] = find(d2 == maxd);
        if maxd < 10
            q = ccw(conn,20);
        else
            state = 7
        end
    %% 着陸シーケンス
    elseif state == 7
        H = rgb2hsv(I);
        B(:,:,1) = (H(:,:,1) < 0.1 | H(:,:,1) > 0.9) & (H(:,:,2) > 0.6) & (H(:,:,3) > 0.18);
        for i=0:1:2
            for j=0:1:2
                d2(i+1,j+1)=sum(sum(B(i*int16(720/3)+1:(i+1)*int16(720/3),j*int16(960/3)+1:(j+1)*int16(960/3))));
            end
        end
        imshow(B)
        maxd = max(max(d2));
        [x,y] = find(d2 == maxd);
        if maxd > 100
            if y == 1
                %moveleft(ryzeObj,0.7,1);
                left(conn,30);
            elseif y == 3
                %moveright(ryzeObj,0.7,1);
                right(conn,30);
            elseif (x==2 || x ==1) && y==2                
                %moveforward(ryzeObj,0.3,1);
                forward(conn,30);
            elseif (x== 3) && y == 2
                if last == 0
                    if(maxd < 10000)
                        %movedown(ryzeObj,0.3,1);
                        down(conn,20);
                    elseif(maxd <30000)
                        %moveforward(ryzeObj,0.5,1);
                        forward(conn,50);
                    else
                        last = 1;
                        %moveforward(ryzeObj,0.5,1);
                        forward(conn,50);
                    end
                else 
                    %if(maximum < 5000)
                    %    break;
                    %else
                    %moveforward(ryzeObj, 0.5,1);
                    forward(conn,40);
                    %end
                end
            end
        else
            if last == 0
                %moveback(ryzeObj,0.5,0.8);
                back(conn,40);
            else
                %break;
                state = 90;
            end
        end
    %% ライントレースシーケンス
    elseif state == 9
        %speed(conn,0.2)
        if(tof > 40)
            down(conn, 20);
        end
        
        % Create Moving Buffer
        d4=zeros(6,5);
        q1 = 0;
        q2x = 0;
        q2y = 0;
        % 画像の取得
        I2 = imcrop(I,[0 361 960 720]);
        H= rgb2hsv(I2);
        U = zeros(360,960);
        D2 = logical(U);
        D3 = logical(U);
        % Red
        D2(:,:,1) = (H(:,:,1) < 0.1 | H(:,:,1) > 0.9) & (H(:,:,2) > 0.7) & (H(:,:,3) > 0.2);
        % Yellow
        D3(:,:,1) = ((H(:,:,1)>0.1 & H(:,:,1)<0.1667) | (H(:,:,1) > 0.833 & H(:,:,1)<0.9)) & (H(:,:,2) > 0.7) & (H(:,:,3) > 0.2);
        % Red Bin
        for i=0:1:5
           for j=0:1:4
              d4(i+1,j+1)=sum(sum(D2(i*int16(360/6)+1:(i+1)*int16(360/6),j*int16(960/5)+1:(j+1)*int16(960/5))));
           end
        end
        % Yellow Bin
        for i=0:1:5
           for j=0:1:4
              d5(i+1,j+1)=sum(sum(D3(i*int16(360/6)+1:(i+1)*int16(360/6),j*int16(960/5)+1:(j+1)*int16(960/5))));
           end
        end       
        % 画像チェック
        
        imshow(D2);
        max14 = max(max(d4(1:4,:)));
        % 全体最大値取得
        maxd = max(max(d4(:,:)))
        maximum = max(d4(6,:)) % 下列最大値取得
        maximum2 = 0; % 下二列次最大値取得
        prevlefthand = sum(sum(d4(:,1:2)));
        prevrighthand = sum(sum(d4(:,4:5)));
        
        % 下列最大位置取得
        if maximum == 0
            q1 = -1
        else
            q1 = find(d4(6,:) == maximum);
        end
        % 下２列次最大値取得
        for i = 5:1:6
           for j = 1:1:5
               m = d4(i,j);
               if(m > maximum && m > maximum2)
                   maximum2 = m;
               elseif( m < maximum && m > maximum2)
                   maximum2 = m;
               end
           end
        end
        % 下２列次２番目最大値取得
        for i = 5:1:6
           for j = 1:1:5
               mk = d4(i,j);
               if(mk ~= maximum) && (mk ~= maximum2)
                   maxi3 = mk;
               else
                   maxi3 =0;
               end
           end
        end
        if maxi3 == 0
            q3x = -1;
            q3y = -1;
        else
           [q3y,q3x] = find(d4(5:6,:) == maxi3);
        end
        if maximum2 == 0
            q2x = -1;
            q2y = -1;
        else
           [q2y,q2x] = find(d4(5:6,:) == maximum2);
        end
       
        if max(d5(6,:)) > 1000
            [sy,sx] = max(d5(6,:));
        else 
            sy = -1;
            sx = -1;
        end
        if max(max(d5)) > 10
            [endy,endx] = max(d5(6,:));
        else 
            endy = -1;
            endx = -1;
        end
        if count > 5 &&  endy == -1
            state = 10;
        elseif sy >0
            if sx<3
                right(conn,20);
                %cw(conn,20);
            else
                left(conn,20);
            end
        elseif maximum <= 10
           if maxd > 100
               %forward(conn, 30);
               %state = 10
               
               if prevlefthand > prevrighthand
                   if (cnt < 3)
                    ccw(conn, 30);
                    cnt = cnt + 1;
                   else
                       cnt = 0;
                       prevlefthand = 0;
                       prevrighthand = 1000;
                   end
               else
                    if (cnt < 3)
                    cw(conn, 30);
                    cnt = cnt + 1;
                   else
                       cnt = 0;
                       prevlefthand = 0;
                       prevrighthand = 1000;
                    end
               end
           else
               pause(4);
               ccw(conn,50);
               if flag == 1
                    back(conn,20);
                    flag = 1
                    count = count +1
               %elseif flag  ==0
                %   pause(2);
                 %  ccw(conn,50);
                  % flag = 2
                   %count = count+1
                  
               else
                   pause(5);
                   cw(conn,30);
                   flag = 0;
                   count = count +1
                   
               end
                   
                   
               %state = 11;
           end
        elseif maximum > 10
            switch q1
                case 1
                    %left(conn,20);
                    ccw(conn,10);
                case 2
                    %if q2x == 1
                        ccw( conn, 5);
                    %else
                    %    left(conn, 20);
                        %cw( conn, 10);
                    
                    %end
                case 3
                    if q2y == 1 && (q2x >=2 && q2x <=4)
                        if(d5(6,2) > 10)
                            right(conn,20);
                            %cw(conn, 5);
                        elseif (d5(6,4) > 10)
                            left(conn,20);
                            %ccw(conn, 5);
                        elseif (d5(6,3) > 10)
                            if(q2x == 2)
                                %left(conn,20);
                                cw(conn,10);
                            elseif(q2x == 4)
                                %right(conn,20);
                                cw(conn,10);
                            else
                                back(conn, 20);
                            end
                        else
                            if max14 > 0
                                forward(conn,30);
                            else
                                if q2x == 2
                                    ccw(conn,45);
                                elseif q2x == 4
                                    cw(conn,45);
                                else
                                    if q3x <3
                                        ccw(conn,10);
                                    else
                                        cw(conn,10);
                                    end
                                end
                            end
                             
                        end
                    elseif q2x == 1 || (q2y == 2 && q2x == 2)
                        ccw(conn, 5);
                    elseif q2x == 5 || (q2y == 2 && q2x == 4)
                        cw(conn, 5);
                    else
              if prevlefthand > prevrighthand
                   if (cnt < 3)
                    ccw(conn, 30);
                    cnt = cnt + 1;
                   else
                       cnt = 0;
                       prevlefthand = 0;
                       prevrighthand = 1000;
                   end
               else
                    if (cnt < 3)
                    cw(conn, 30);
                    cnt = cnt + 1;
                   else
                       cnt = 0;
                       prevlefthand = 0;
                       prevrighthand = 1000;
                    end
               end
                        %state = 10
                    end
                case 4
                    %if q2x == 5
                        cw(conn, 5);
                    %else
            %end
                case 5
                    %right(conn, 20);
                    cw(conn,10);
            end
        else
              if prevlefthand > prevrightand
                   if (cnt < 3)
                    ccw(conn, 40);
                    cnt = cnt + 1;
                   else
                       cnt = 0;
                       prevlefthand = 0;
                       prevrighthand = 1000;
                   end
               else
                    if (cnt < 3)
                    cw(conn, 40);
                    cnt = cnt + 1;
                   else
                       cnt = 0;
                       prevlefthand = 0;
                       prevrighthand = 1000;
                    end
               end
            %land(conn);
            %break;
        end
        
        prevlefthand = lefthand;
        prevrighthand = righthand;
        
   %%窓通過後のロープまで 
    elseif state==8
        %"hoge"
         H = rgb2hsv(I);
         B(:,:,1) = (H(:,:,1) < 0.05 | H(:,:,1) > 0.95) & (H(:,:,2) > 0.5) & (H(:,:,3) > 0.2);
         %B(:,:,1) = (H(:,:,1) < 0.1 | H(:,:,1) > 0.9) & (H(:,:,2) > 0.7) & (H(:,:,3) > 0.5);
        for i=0:1:4
            for j=0:1:4
                d3(i+1,j+1)=sum(sum(B(i*int16(720/5)+1:(i+1)*int16(720/5),j*int16(960/5)+1:(j+1)*int16(960/5))))
            end
        end
        imshow(B)
        maximum3 = max(max(d3))
        
        if maximum3 == 0
            x = -1;
            y = -1;
        else
           [x,y] = find(d3 == maximum3) 
        end
        %flag2=1;
     %ロープ見つけるまで少しずつ左に移動
       if (maximum3 < 10) && flag2==1
            left(conn,20);
     
     %ロープを見つけ、中心に来るように移動、ある程度進んだあと下がる
       elseif maximum3 >= 10 && flag2==1
            if  y ==1
                left(conn,20);
            elseif  (y==4 || y ==5) 
                right(conn,20);
            elseif (y==3||y==2)
                %調整必須
                if(tof <= 40 || maximum3 < 1000)
                 forward(conn,200);
                % forward(conn,50);
                elseif tof>40
                    "ghoge"
                  down(conn, 30);
                end
                if(maximum3 >2000  && tof <= 40)
                    flag2=2
                end
            end
            
         
           
        %正確に寄っていく
       elseif maximum3 >= 10 && flag2==2
           %ｙを中心にさせ、進む
           if  y ==1          
               if (maximum3 < 4000 )
                   "l"
                cw(conn, -20);
               elseif (x== 5) && (maximum3 > 4000 ) 
                   "l2"
                cw(conn, -15);
                flag2=3;
               else
                   "p"
                cw(conn, -15);   
               end
               
           elseif y == 2
               "l3"
                right(conn,20);
              
           elseif  (y==4 || y ==5)
               "l4"
            right(conn,25);
           elseif  y==3 
                 if (x== 5) && (maximum3 < 2000)
                     "l5"
                    forward(conn,30);
                 elseif (x== 5) &&(maximum3 <20000)
                     "l6"
                    %moveforward(ryzeObj,0.3,1);
                    down(conn,20);
                    %turn(ryzeObj,deg2rad(-15));
                    flag2=3;
               
                 elseif(x~=5 ) && ( (maximum3 <20000))
                     "l7"
                    forward(conn,20);
                end
             
           end
           %座標をx2,y2に記録
           x2=x;
           y2=y;
           %forward(conn,20);
           
      %ロープを失ったら前の記憶を基に角度を変え、少し下がる
      elseif (maximum3 < 10) && flag2==2
            if (y2==2 || y2 ==1)
                "l8"
                cw(conn, -30);
                %back(conn,20);
            elseif (y2==4 || y2 ==5)
                "l9"
                cw(conn, 30);
                %back(conn,20);
            elseif y2==3    
                %back(conn,20);
            end
       elseif flag2==3
           state=13;
       pause(5);               
       end
       %ライントレース準備
    elseif state == 13
        I2 = imcrop(I,[60 361 839 720]);
        H= rgb2hsv(I2);
        % Red
        D2(:,:,1) = (H(:,:,1) < 0.1 | H(:,:,1) > 0.9) & (H(:,:,2) > 0.7) & (H(:,:,3) > 0.2);
        
        % Red Bin
        for i=0:1:5
           for j=0:1:4
              d4(i+1,j+1)=sum(sum(D2(i*int16(360/6)+1:(i+1)*int16(360/6),j*int16(840/5)+1:(j+1)*int16(840/5))));
           end
        end
        max4 = max(max(d4));
        if max4 <= 0
            xnew = -1;
            ynew = -1;
        else
            [ynew,xnew] = find(d4 == max4);
        end
        if xnew >3 
            cw(conn,30);
        elseif xnew<3
            ccw(conn,30);
        else
            state = 9;
        end
            
        
        
        
      %着艦準備state = 10
    elseif state == 10
        up(conn,50);
        if(tof >100)
            state = 11;
        end
    elseif state == 11
        pause(3);
        forward(conn,150);
        state = 12;
    elseif state == 12
        pause(3);
        ccw(conn,35);
        state = 6;   
     else
        land(conn);
        if(strcmp(q, 'ok'))
            break;
        end
    end
    pause(0.1);




end             


%%
% Command Set
function [J] = getState(c)
    J = c.fromRedis('state')
end

function q = motoron(c)
    q = c.toRedis('motoron');
    q = native2unicode(q, 'UTF-8');
    if(strcmp(q,'ok'))
        'motoron'
    end
end
function q = takeoff(c)
    q = c.toRedis('takeoff');
    q = native2unicode(q, 'UTF-8');
    if(strcmp(q,'ok'))
        'takeoff'
    end
end
function q = land(c)
    q = c.toRedis('land');
    q = native2unicode(q, 'UTF-8');
    if(strcmp(q,'ok'))
        'land'
    end
end
function q = emergency(c)
    q = c.toRedis('emergency');
    q = native2unicode(q, 'UTF-8');
    if(strcmp(q,'ok'))
        'emergency'
    end
end
function q = up(c,x)
    s = ['up ' num2str(x,'%d')];
    q = c.toRedis(s);
    q = native2unicode(q, 'UTF-8');
    if(strcmp(q,'ok'))
        'up'
    end
end
function q = down(c,x)
    s = ['down ' num2str(x,'%d')];
    q = c.toRedis(s);
    q = native2unicode(q, 'UTF-8');
    if(strcmp(q,'ok'))
        'down'
    end
end
function q = left(c,x)
    s = ['left ' num2str(x,'%d')];
    q = c.toRedis(s);
    q = native2unicode(q, 'UTF-8');
    if(strcmp(q,'ok'))
        'left'
    end
end
function q = right(c,x)
    s = ['right ' num2str(x,'%d')];
    q = c.toRedis(s);
    q = native2unicode(q, 'UTF-8');
    if(strcmp(q,'ok'))
        'right'
    end
end
function q = forward(c,x)
    s = ['forward ' num2str(x,'%d')];
    q = c.toRedis(s);
    q = native2unicode(q, 'UTF-8');
    if(strcmp(q,'ok'))
        'forward'
    end
end
function q = back(c,x)
    s = ['back ' num2str(x,'%d')];
    q = c.toRedis(s);
    q = native2unicode(q, 'UTF-8');
    if(strcmp(q,'ok'))
        'back'
    end
end
function q = cw(c,x)
    s = ['cw ' num2str(x,'%d')];
    q = c.toRedis(s);
    q = native2unicode(q, 'UTF-8');
    if(strcmp(q,'ok'))
        'cw'
    end
end
function q = ccw(c,x)
    s = ['ccw ' num2str(x,'%d')];
    q = c.toRedis(s);
    q = native2unicode(q, 'UTF-8');
    if(strcmp(q,'ok'))
        'ccw'
    end
end
function q = flip(c,x) % x: 'l' = left, 'r' = right, 'f' = forward, 'b' = back
    s = ['flip ' x];
    q = c.toRedis(s);
    q = native2unicode(q, 'UTF-8');
    if(strcmp(q,'ok'))
        'flip'
    end
end
function q = go(c,x, y, z, s) % speed; cm/s
    s = strcat('go ', num2str(x,'%d'), ' ',num2str(y,'%d'), ' ',num2str(z,'%d'), ' ',num2str(s,'%d'));
    q = c.toRedis(s);
    q = native2unicode(q, 'UTF-8');
    if(strcmp(q,'ok'))
        'go'
    end
end
function q = stop(c)
    q = c.toRedis('stop')
    q = native2unicode(q, 'UTF-8');
    if(strcmp(q,'ok'))
        'stop'
    end
end
function q = speed(c,x)
    s = ['speed ' num2str(x,'%d')];
    q = c.toRedis(s);
    q = native2unicode(q, 'UTF-8');
    if(strcmp(q,'ok'))
        'speed'
    end
end
function q = rc(c,rl,ph,th,yw)
    s = strcat('rc ', num2str(rl,'%d'), ' ',num2str(ph,'%d'), ' ',num2str(th,'%d'), ' ',num2str(yw,'%d'));
    q = c.toRedis(s);
    q = native2unicode(q, 'UTF-8');
    if(strcmp(q,'ok'))
        'rc'
    end
end
