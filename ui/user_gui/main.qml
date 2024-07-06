import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import "qml"

Window {
    width: 1366
    height: 728
    visible: true
    title: qsTr("Delta X")
    //flags: Qt.Window | Qt.FramelessWindowHint

    Popup {
        id: inputPassPopup

        parent: Overlay.overlay

        x: Math.round((parent.width - width) / 2)
        y: Math.round((parent.height - height) / 2)
        width: 320
        height: 180

        Text {
            text: qsTr("Master password")
            anchors.top: parent.top
            anchors.topMargin: 0
            anchors.horizontalCenter: parent.horizontalCenter
            font.pointSize: 20
        }

        TextField {
            id: masterPassInput
            text: qsTr("")
            anchors.top: parent.top
            anchors.topMargin: 50
            anchors.horizontalCenter: parent.horizontalCenter
            echoMode: TextInput.Password

            font.pointSize: 18
            height: 36
            width: 190

        }

        Button {
            font.pointSize: 18
            width: 130
            height: 50
            text: "Done"
            anchors.left: parent.left
            anchors.bottom: parent.bottom
            anchors.leftMargin: 0
            anchors.bottomMargin: 0

            background: Rectangle {
                color: (!parent.down)?"#bfe2a2":"#b112a2"
                radius: 10

            }

            onClicked: {
                if (masterPassInput.text === masterPass) {
                    if (homePannel.visible == true) {
                        homePannel.visible = false
                        settingPannel.visible = true
                    }

                    masterPassInput.text = ""
                    inputPassPopup.close()
                }
            }
        }


        Button {
            font.pointSize: 18
            width: 130
            height: 50
            text: "Cancel"
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.rightMargin: 0
            anchors.bottomMargin: 0

            background: Rectangle {
                color: (!parent.down)?"#bfe2a2":"#b112a2"
                radius: 10

            }
            onClicked: {
                inputPassPopup.close()
            }
        }
    }


    Rectangle {
        id: homePannel
        color: "#e9e9e9"
        anchors.fill: parent
        anchors.margins: 2
        visible: true

        Image {
            id: logoImage
            anchors.top: parent.top
            anchors.left: parent.left
            source: "images/delta-logo-color.png"
            fillMode: Image.PreserveAspectFit
            width: 300
        }

        Rectangle {
            anchors.left: logoImage.right
            anchors.top: parent.top
            anchors.bottom: logoImage.bottom
            anchors.topMargin: 5
            width: 440
            color: "#00ffffff"
            anchors.leftMargin: 40


            Grid {
                anchors.fill: parent
                anchors.leftMargin: 2
                spacing: 15
                verticalItemAlignment: Grid.AlignVCenter
                horizontalItemAlignment: Grid.AlignLeft
                rows: 2
                columns: 6

                Rectangle {
                    width: 30
                    height: 19
                    color: "#6c1414"
                    radius: 8
                    objectName: "robot1State"
                }

                Text {
                    text: qsTr(":Robot 1")
                    font.pointSize: 14
                }

                Rectangle {
                    width: 30
                    height: 19
                    color: "#6c1414"
                    radius: 8
                    objectName: "robot2State"
                }

                Text {
                    text: qsTr(":Robot 2")
                    font.pointSize: 14
                }

                Rectangle {
                    width: 30
                    height: 19
                    color: "#6c1414"
                    radius: 8
                    objectName: "cameraState"
                }

                Text {
                    text: qsTr(":Camera")
                    font.pointSize: 14
                }

                Rectangle {
                    width: 30
                    height: 19
                    color: "#6c1414"
                    radius: 8
                    objectName: "conveyor1State"
                }

                Text {
                    text: qsTr(":Conveyor 1")
                    font.pointSize: 14
                }

                Rectangle {
                    width: 30
                    height: 19
                    color: "#6c1414"
                    radius: 8
                    objectName: "conveyor2State"
                }

                Text {
                    //text: qsTr(":Conveyor 2")
                    text: qsTr(":Encoder")
                    font.pointSize: 14
                }

                Rectangle {
                    width: 30
                    height: 19
                    color: "#6c1414"
                    radius: 8
                    objectName: "serverState"
                }

                Text {
                    text: qsTr(":Server")
                    font.pointSize: 14
                }
            }
        }

        Rectangle {
            id: rectangleBox
            anchors.bottom: imageLabel.top
            anchors.leftMargin: 40
            anchors.topMargin: 40

            anchors.top: logoImage.bottom
            width: 500
            radius: 10
            anchors.left: parent.left
            anchors.bottomMargin: 30

            Rectangle {
                id: rectangle2
                anchors.verticalCenter: parent.verticalCenter
                width: 150
                height: 100
                color: "#c5d7ff"
                radius: 6
                anchors.left: parent.left
                anchors.leftMargin: 60

                Text {
                    text: qsTr("Box 1")
                    font.pointSize: 14
                    anchors.top: parent.top
                    anchors.left: parent.left
                    anchors.leftMargin: 6
                }

                Rectangle {
                    objectName: "box1FiberSensor"
                    width: 20
                    height: 20
                    color: "#636363"
                    anchors.right: parent.right
                    anchors.rightMargin: 6
                    anchors.top: parent.top
                    anchors.topMargin: 6
                    radius: 9
                }

                Text {
                    text: qsTr("6")
                    objectName: "box1NumberText"
                    anchors.horizontalCenter: parent.horizontalCenter
                    font.pointSize: 35
                    anchors.bottom: parent.bottom
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    font.styleName: "Bold"
                    anchors.bottomMargin: 10
                }
            }

            Rectangle {
                anchors.verticalCenter: parent.verticalCenter
                width: 150
                height: 100
                color: "#c5d7ff"
                radius: 6
                anchors.right: parent.right
                anchors.rightMargin: 60

                Text {
                    text: qsTr("Box 2")
                    font.pointSize: 14
                    anchors.top: parent.top
                    anchors.left: parent.left
                    anchors.leftMargin: 6
                }

                Rectangle {
                    objectName: "box2FiberSensor"
                    width: 20
                    height: 20
                    color: "#636363"
                    anchors.right: parent.right
                    anchors.rightMargin: 6
                    anchors.top: parent.top
                    anchors.topMargin: 6
                    radius: 9
                }

                Text {
                    text: qsTr("6")
                    objectName: "box2NumberText"
                    anchors.horizontalCenter: parent.horizontalCenter
                    font.pointSize: 35
                    anchors.bottom: parent.bottom
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    font.styleName: "Bold"
                    anchors.bottomMargin: 10
                }
            }
        }

        Rectangle {
            id: conveyorSpeedBox
            anchors.verticalCenter: rectangleBox.verticalCenter
            anchors.left: rectangleBox.right
            width: 300
            height: 90
            color: "#00ffffff"
            anchors.leftMargin: 40
            visible: true

            Text {
                text: qsTr("Conveyor 1 Speed: 200 mm/s")
                objectName: "conveyor1SpeedText"
                font.pointSize: 15
                anchors.top: parent.top
            }

            Text {
                text: qsTr("Encoder Speed: 200 mm/s")
                objectName: "encoderSpeedText"
                font.pointSize: 15
                anchors.verticalCenter: parent.verticalCenter
            }

            Text {
                x: 0
                y: 62
                text: qsTr("Conveyor 2 Speed: 200 mm/s")
                objectName: "conveyor2SpeedText"
                font.pointSize: 15
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 1
            }
        }

        Text {
            id: timeForFrameText
            objectName: "timeForFrameText"
            text: qsTr("0.5 ms")
            anchors.bottom: imageLabel.top
            anchors.left: parent.left
            font.pointSize: 14
            anchors.leftMargin: 100
            visible: true
        }

        Rectangle {
            id: placeProfileGroupt
            clip: true
            anchors.top: imageLabel.top
            anchors.right: imageLabel.right
            anchors.topMargin: 40
            anchors.rightMargin: 20
            width: 400
            height: 180
            radius: 5
            border.width: 1

            Text {
                id: activeProfileText
                objectName: "activeProfileText"
                text: qsTr("ActiveProfile: Box1")
                anchors.top: parent.top
                anchors.left: parent.left
                font.pointSize: 18
                anchors.leftMargin: 10
                anchors.topMargin: 20
            }

            ComboBox {
                id: placeProfilesMain
                height: 48
                font.pointSize: 18
                width: 200
                model: ["0.5 mm", "1 mm", "5 mm", "10 mm", "50 mm"]
                anchors.left: parent.left
                anchors.leftMargin: 10
                anchors.top: parent.top
                anchors.topMargin: 70

                objectName: "placeProfilesMain"
            }

            Button {
                font.pointSize: 18
                width: 130
                height: 50
                text: "Select"
                anchors.verticalCenter: placeProfilesMain.verticalCenter
                anchors.left: placeProfilesMain.right
                anchors.leftMargin: 20

                background: Rectangle {
                    color: (!parent.down)?"#bfe2a2":"#b112a2"
                    radius: 10

                }

                objectName: "selectProfile"
            }
        }

        Image {
            id: imageLabel
            objectName: "imageLabel"

            anchors.left: parent.left
            anchors.bottom: parent.bottom
            anchors.leftMargin: 100
            fillMode: Image.PreserveAspectFit
            height: 400
            width: height * 3 / 2
            visible: true
        }

        Button {
            font.pointSize: 15
            width: 70
            height: 40
            text: "Show"

            anchors.bottom: parent.bottom
            anchors.bottomMargin: 10
            anchors.left: parent.left
            anchors.leftMargin: 10

            background: Rectangle {
                color: (!parent.down)?"#bfe2a2":"#b112a2"
                radius: 10

            }

            onClicked: {
                if (imageLabel.visible === false){
                    imageLabel.visible = true
                    timeForFrameText.visible = true
                    conveyorSpeedBox.visible = true
                }
                else {
                    imageLabel.visible = false
                    timeForFrameText.visible = false
                    conveyorSpeedBox.visible = false
                }
            }
        }

        Rectangle {
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: 430
            width: 460
            border.width: 1
            radius: 10
            anchors.bottomMargin: 70

            Label {
                id: objectLabel
                objectName: "objectLabel"
                anchors.fill: parent
                anchors.margins: 10
                font.pointSize: 12
                text: "- M, x, y, angle"
            }
        }

        Text {
            text: qsTr("Counter:")
            font.pointSize: 35
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            font.styleName: "Bold"
            anchors.bottom: parent.bottom
            anchors.right: boxCounter.left
            anchors.rightMargin: 90
        }

        Text {
            id: boxCounter
            text: qsTr("6099")
            objectName: "boxCounter"
            font.pointSize: 35
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            font.styleName: "Bold"
            anchors.bottom: parent.bottom
            anchors.right: parent.right
            anchors.rightMargin: 90
        }

        Button {
            id: settingBtn
            objectName: "settingBtn"
            anchors.right: startBtn.left
            anchors.top: parent.top
            anchors.topMargin: 20
            anchors.rightMargin: 70
            font.pointSize: 25
            display: AbstractButton.TextOnly
            width: 150
            height: 50
            text: "Settings"
            visible: (startBtn.text === "Start")?true:false

            background: Rectangle {
                color: "#bfe2a2"
                radius: 10

            }
            onClicked: {
                inputPassPopup.open()


            }
        }

        Button {
            id: startBtn
            objectName: "startBtn"
            anchors.right: parent.right
            anchors.top: parent.top
            font.pointSize: 50
            display: AbstractButton.TextOnly
            width: 320
            height: 180
            text: "Start"

            background: Rectangle {
                color: (startBtn.text === "Start")?"#bdf7ff":"#fa8072"
                radius: 20

            }
            // onClicked: {
            //     if (text === "Start") {
            //         text = "Stop"

            //     }
            //     else {
            //         text = "Start"
            //     }
            // }
        }
    }

    Rectangle {
        id: settingPannel
        color: "#e9e9e9"
        anchors.fill: parent
        anchors.margins: 2
        visible: false

        Rectangle {
            id: controlPannel
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            height: 250
            color: "#e9e9e9"
            anchors.leftMargin: 3

            Row {
                id: row
                anchors.fill: parent
                spacing: 5

                RobotControl {
                    device_name: "Robot 1"
                    objectName: "robot1controler"
                    enabled: (calibView.currentIndex === 5)?false:true
                }

                RobotControl {
                    device_name: "Robot 2"
                    objectName: "robot2controler"
                    enabled: (calibView.currentIndex === 4)?false:true
                }

                ConveyorControl {
                    objectName: "conveyor1controler"
                    device_name: "Conveyor 1"
                }

                ConveyorControl {
                    objectName: "conveyor2controler"
                    device_name: "Conveyor 2"
                }
            }
        }

        SwipeView {
            id: calibView
            anchors.top: controlPannel.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            currentIndex: 0
            clip: true

            CalibStep1 {

            }

            CalibStep2 {

            }

            CalibStep3 {

            }

            CalibStep31 {

            }

            CalibStep4 {

            }

            CalibStep5 {

            }

            CalibStep6 {

            }

            Component.onCompleted: {
                calibView.currentIndex = 0
            }

            
        }

        PageIndicator {
            id: indicator

            count: calibView.count
            currentIndex: calibView.currentIndex
            anchors.rightMargin: 200
            anchors.bottom: calibView.bottom
            transformOrigin: Item.Center
            scale: 1.5
            anchors.right: calibView.right
        }

        Button {
            id: reloadImageBtn
            objectName: "reloadImageBtn"
            icon.height: 24
            icon.width: 24
            icon.source: "images/icons8-synchronize-24.png"

            font.pointSize: 25
            display: AbstractButton.IconOnly
            width: 60
            height: 60
            text: "Reload"

            anchors.left: parent.left
            anchors.verticalCenter: homePannelBtn.verticalCenter
            anchors.leftMargin: 10

            visible: (calibView.currentIndex === 6)?false:true

            background: Rectangle {
                color: (!parent.down)?"#bfe2a2":"#b112a2"
                radius: 10

            }
            onClicked: {
                
            }
        }

        Text {
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 5
            width: 400
            font.pointSize: 14
            anchors.left: parent.left
            text: ""
            id: pointBufferText
            anchors.leftMargin: 10
            objectName: "currentPointLog"
        }

        Text {
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 5
            font.pointSize: 14
            anchors.left: pointBufferText.right
            text: ""
            anchors.rightMargin: 60
            objectName: "currentEncoderLog"
        }

        Button {
            id: homePannelBtn
            objectName: "homePannelBtn"
            anchors.right: parent.right
            anchors.top: parent.top
            icon.height: 32
            icon.width: 32
            font.hintingPreference: Font.PreferDefaultHinting
            icon.source: "images/icons8-home-32.png"
            anchors.topMargin: 260
            anchors.rightMargin: 10
            font.pointSize: 25
            display: AbstractButton.TextBesideIcon
            width: 150
            height: 50
            text: "Home"

            background: Rectangle {
                color: "#bfe2a2"
                radius: 10

            }
            onClicked: {
                if (settingPannel.visible == true) {
                    settingPannel.visible = false
                    homePannel.visible = true
                }


            }
        }



        Button {
            id: saveCalibBtn
            objectName: "saveCalibBtn"
            anchors.right: homePannelBtn.left
            icon.height: 32
            icon.width: 32
            icon.source: "images/icons8-save-32.png"

            anchors.rightMargin: 170
            font.pointSize: 25
            display: AbstractButton.TextBesideIcon
            width: 150
            height: 50
            text: "Save"
            anchors.verticalCenter: homePannelBtn.verticalCenter

            background: Rectangle {
                color: (!parent.down)?"#bfe2a2":"#b112a2"
                radius: 10

            }
            onClicked: {

            }
        }

        Button {
            id: nextCalibBtn
            objectName: "nextCalibBtn"
            anchors.bottom: parent.bottom
            anchors.horizontalCenter: homePannelBtn.horizontalCenter
            icon.height: 30
            icon.width: 30
            icon.source: "images/icons8-next-30.png"
            anchors.bottomMargin: 10
            font.pointSize: 25
            display: AbstractButton.TextBesideIcon
            width: 140
            height: 50
            text: "Next"

            enabled: (calibView.currentIndex < calibView.count - 1)?true:false

            background: Rectangle {
                color: (!parent.down)?"#bfe2a2":"#b112a2"
                radius: 10

            }
            onClicked: {
                calibView.currentIndex++
            }
        }

        Button {
            id: backCalibBtn
            objectName: "backCalibBtn"
            icon.height: 30
            icon.width: 30
            icon.source: "images/icons8-back-30.png"
            font.pointSize: 25
            display: AbstractButton.TextBesideIcon
            width: 140
            height: 50
            text: "Back"
            anchors.verticalCenter: nextCalibBtn.verticalCenter
            anchors.horizontalCenter: saveCalibBtn.horizontalCenter

            enabled: (calibView.currentIndex == 0)?false:true

            background: Rectangle {
                color: (!parent.down)?"#bfe2a2":"#b112a2"
                radius: 10

            }
            onClicked: {
                calibView.currentIndex--
            }
        }
    }
}
