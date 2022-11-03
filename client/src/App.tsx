import { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

interface obj {
  confidence: number;
  meaning: string;
  model: string;
}

interface data {
  ID: number;
  time: string;
  objects: obj[];
}
function App() {
  const [video, setVideo] = useState("");
  const [recall, setRecall] = useState(0);
  const [results, setResults] = useState<data[]>([]);

  useEffect(() => {
    getObjectMeaning();
    setTimeout(() => setRecall(recall + 1), 2000);
  }, [recall]);

  const contorlWebcam = async (toggle: string) => {
    await axios({
      url: "/webcam",
      method: "post",
      data: {
        webcam: toggle,
      },
    }).then((res) => {
      if (res.data === "open") {
        setVideo("/video");
      } else {
        setVideo("");
      }
    });
  };

  const getObjectMeaning = async () => {
    await axios.get<data[]>("/results").then((res) => {
      setResults(res.data);
      console.log(res.data);
    });
  };

  return (
    <>
      <div className="flex items-center pt-5 flex-col">
        <div className="text-4xl pb-5">
          A robust system for recognizing the meaning of objects in video
          streams
        </div>
        <div className="flex flex-row">
          <button
            className="rounded-lg p-3 m-3 bg-sky-400 text-white hover:bg-sky-600"
            onClick={() => contorlWebcam("open")}
          >
            Turn on the Webcam
          </button>
          <button
            className="rounded-lg p-3 m-3 bg-sky-400 text-white hover:bg-sky-600"
            onClick={() => contorlWebcam("close")}
          >
            Turn off the Webcam
          </button>
        </div>
        <div className="flex flex-row">
          <img src={video} className="h-[500px]" />
          <Table results={results} />
        </div>
      </div>
    </>
  );
}

type Props = {
  results: data[];
};
const Table = ({ results }: Props) => {
  return (
    <table className="border-collapse border h-full w-[250px] mb-2">
      <thead className="bg-sky-400">
        <tr>
          <th>ID</th>
          <th>Time</th>
          <th>Meaning</th>
        </tr>
      </thead>
      <tbody>
        {results.map((data) => {
          return (
            <tr>
              <th>{data.ID}</th>
              <td>{data.time}</td>
              <td>
                {data.objects.map((obj) => {
                  return (
                    <div className="flex flex-col items-center justify-center border-l-[1px] border-sky-100">
                      {obj.meaning}
                    </div>
                  );
                })}
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
};

export default App;
