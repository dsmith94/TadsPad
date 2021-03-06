
TADSPAD v0.1 Early Beta release

TO BE FIXED:
* As yet, installing TADS/ADV3LITE is a very manual process. I'd like to write an installer to make it easier for new users.
* The Transcript system is quite basic at this point. It'd be great to make it so users could save a transcript they use a lot and reload it later.
* Lots of beta testing, thusly followed by lots of bugfixes.



  == Welcome ==
  
  Hello and welcome to TadsPad! This project began as a simple editor to write TADS games on my linux laptop. As I worked on this thing, it grew and grew and now has way more features than it was ever intended to. That said, I think it works pretty well, to the point where I have a hard time using Tads Workbench.
  
  Having said that, it's pretty simple. If you can use Notepad, you can pretty much use TadsPad. If you're new to TADS, TadsPad can be a handy tool for learning the language, because of the built-in code completion and context sensitive help.
  
  TadsPad is a cross platform Scintilla-based editor implemented in Python 2.7 with wxPython. If you have Python 2.7, the wxPython library, a working installation of TADS 3.1 and Adv3Lite, and a reasonably fast computer, TadsPad should run like a champ.
  
  
  
  == Features ==
  
  * Adv3Lite! Actually, the editor is built entirely around Eric Eve's excellent library. You could maybe make it work with Adv3, but it's probably more trouble than it's worth. (I've tried and failed miserably.)
  * Editor Color themes! Because the default on TADS Workbench hurts my eyes. Default is based on Gedit's Oblivion theme. TadsPad's version of Scintilla comes with a TADS 3 language lexer built in, so it should highlight properly. The theming system is (mostly) compatible with Eclipse themes, so if you have one of the bajillion Eclipse themes that you really like, you should be able to just plug it in by copying it to the TadsPad themes directory and loading it from inside TadsPad.
  * Context Sensitive Help! This is something I've thought TADS has needed for a long time. The system is so big and so complex that having Insta-Help saves me the trouble of cross-referencing in the Library Reference every 5 minutes.
  * Code Completion! TADS is a very structured, classic C-style language. Happily, this makes code completion easier to write than for a natural language system. I've re-written the code analysis engine like four times, and the present design works pretty good.
  * Object Browser! It's common for TADS authors to skip around quite a bit. TadsPad analyzes your code with every save, and produces a complete list of the objects used in your game. Double click one of the objects, and the editor pulls it up for you no matter which file you've stuck it in.
  * Spell checker! And it works! On any platform! If you have the Internet hooked up anyway. Click the Spell Checker item on the tools menu and TadsPad will hurl all the strings (double and single quotes) to After the Deadline, a Spell/Grammer check Internet service.
