import 'dart:convert';
import 'package:image_picker/image_picker.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:io';
import 'package:path/path.dart';
import 'package:async/async.dart';
import 'package:rflutter_alert/rflutter_alert.dart';


String txt = "";
String txt1 = "Upload or take a picture of a bear to classify it";
void main() {
  runApp(new MaterialApp(
    debugShowCheckedModeBanner: false,
    title: "Bear Classifier",
    home: new MyApp(),
  ));
}

class MyApp extends StatefulWidget {
  @override
  _MyAppState createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  File img;
  TextEditingController _textFieldController = TextEditingController();


  // The fuction which will upload the image as a file
  void upload(File imageFile) async {
    var stream =
    new http.ByteStream(DelegatingStream.typed(imageFile.openRead()));
    var length = await imageFile.length();

    String base =
        "https://your-render-app.onrender.com";

    var uri = Uri.parse(base + '/analyze');

    var request = new http.MultipartRequest("POST", uri);
    var multipartFile = new http.MultipartFile('file', stream, length,
        filename: basename(imageFile.path));
    //contentType: new MediaType('image', 'png'));

    request.files.add(multipartFile);
    var response = await request.send();
    print(response.statusCode);
    response.stream.transform(utf8.decoder).listen((value) {
      print(value);
      int l = value.length;
      txt = value;

      setState(() {});
    });
  }

  void user_signup()
  {
    //enter your firebase signup code here
    //https://firebase.google.com/docs/flutter/setup

    //enter your stripe checkout code
    //www.stripe.com

    //Ideally these should be separate forms, but this
    //is just a starter template
  }

  void user_login()
  {
    //Enter firebase login here
  }

  void image_picker(int a) async {
    txt1 = "";
    setState(() {

    });
    debugPrint("Image Picker Activated");
    if (a == 0){
      img = await ImagePicker.pickImage(source: ImageSource.camera);
    }
    else{
      img = await ImagePicker.pickImage(source: ImageSource.gallery);
    }

    txt = "Analysing...";
    debugPrint(img.toString());
    upload(img);
    setState(() {});
  }

  _loginpopup(BuildContext context) async {


    Alert(
        context: context,
        title: "LOGIN",
        content: Column(
          children: <Widget>[
            TextField(
              decoration: InputDecoration(
                icon: Icon(Icons.account_circle),
                labelText: 'Username',
              ),
            ),
            TextField(
              obscureText: true,
              decoration: InputDecoration(
                icon: Icon(Icons.lock),
                labelText: 'Password',
              ),
            ),
          ],
        ),
        buttons: [
          DialogButton(
            onPressed: () => user_login(),
            child: Text(
              "LOGIN",
              style: TextStyle(color: Colors.white, fontSize: 20),
            ),
          ),
          DialogButton(
            onPressed: () => _signuppopup(context),
            child: Text(
              "SIGNUP",
              style: TextStyle(color: Colors.white, fontSize: 20),
            ),
          )
        ]).show();


  }
  _signuppopup(BuildContext context) async {
    Alert(
        context: context,
        title: "SIGNUP",
        content: Column(
          children: <Widget>[
            TextField(
              decoration: InputDecoration(
                icon: Icon(Icons.account_circle),
                labelText: 'Username',
              ),
            ),
            TextField(
              obscureText: true,
              decoration: InputDecoration(
                icon: Icon(Icons.lock),
                labelText: 'Password',
              ),
    ),
            TextField(
              obscureText: true,
              decoration: InputDecoration(
                icon: Icon(Icons.lock),
                labelText: 'First & Last Name',
              ),

            ),
            TextField(
              obscureText: true,
              decoration: InputDecoration(
                icon: Icon(Icons.lock),
                labelText: 'Credit/Debit Card Number',
              ),

            ),
            TextField(
              obscureText: true,
              decoration: InputDecoration(
                icon: Icon(Icons.lock),
                labelText: 'CVV2',
              ),

            ),
            TextField(
              obscureText: true,
              decoration: InputDecoration(
                icon: Icon(Icons.lock),
                labelText: 'Exp Date XX/YY',
              ),

            ),
          ],
        ),
        buttons: [

          DialogButton(
            onPressed: () => user_signup(),
            child: Text(
              "SIGNUP",
              style: TextStyle(color: Colors.white, fontSize: 20),
            ),
          )
        ]).show();
  }


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: new AppBar(
        centerTitle: true,
        title: new Text("Bear Classifier"),
      ),
      body: new Container(
        child: Center(
          child: Column(
            children: <Widget>[
              img == null
                  ? new Text(
                "",
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 32.0,
                ),
              )
                  : new Image.file(img,
                  height: MediaQuery.of(context).size.height * 0.6,
                  width: MediaQuery.of(context).size.width * 0.8),
              new Text(
                txt,
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 32.0,
                ),
              ),
              RaisedButton(
                child: Text('User Authentication'),
                color: Colors.white,

                onPressed: () => _loginpopup(context),
              ),

            ],
          ),
        ),
      ),
      floatingActionButton: new Stack(
        children: <Widget>[
          Align(
              alignment: Alignment(1.0, 1.0),
              child: new FloatingActionButton(
                onPressed: (){
                  image_picker(0);
                },
                child: new Icon(Icons.camera_alt),
              )
          ),
          Align(
              alignment: Alignment(1.0, 0.8),
              child: new FloatingActionButton(
                  onPressed: (){
                    image_picker(1);
                  },
                  child: new Icon(Icons.file_upload)
              )
          ),
        ],
      ),
    );
  }
}
